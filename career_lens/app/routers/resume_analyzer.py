"""
Resume Analyzer API Router

Endpoints for analyzing resumes and extracting career-relevant information.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
import io

from app.models.careers import ResumeAnalyzeResponse
from app.utils.nlp_utils import extract_skills_from_text, analyze_resume
from app.services.skill_progress import get_skill_progress_service
from app.services.groq_service import get_groq_service, is_groq_available
from app.database.db import CAREER_DATA

# Try to import PDF libraries
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    try:
        import PyPDF2
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False

router = APIRouter(prefix="/api", tags=["Resume"])


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text content from a PDF file."""
    try:
        # Try pdfplumber first
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text
    except ImportError:
        pass
    
    try:
        # Fall back to PyPDF2
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except ImportError:
        pass
    
    raise HTTPException(
        status_code=500, 
        detail="PDF processing library not available. Install pdfplumber or PyPDF2."
    )


@router.post("/resume-analyze", response_model=ResumeAnalyzeResponse)
async def analyze_resume_file(
    file: UploadFile = File(...),
    target_career: Optional[str] = Form(None)
):
    """
    Analyze an uploaded resume for skills and career readiness.
    
    - **file**: PDF resume file
    - **target_career**: Optional target career to check readiness against
    
    Returns detected skills, career readiness, and suggestions.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are supported"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Extract text from PDF
        text = extract_text_from_pdf(content)
        
        if not text or len(text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract enough text from PDF"
            )
        
        # Analyze resume
        analysis = analyze_resume(text)
        skills = analysis["skills"]
        recommended_careers = analysis["recommended_careers"]
        
        # Calculate career readiness if target career specified
        matching_skills = []
        missing_skills = []
        career_readiness = 0
        suggestions = []
        
        if target_career:
            service = get_skill_progress_service()
            gap_result = service.analyze_skill_gap(target_career, skills)
            
            if "error" not in gap_result:
                matching_skills = gap_result["current_skills"]
                missing_skills = gap_result["missing_skills"]
                career_readiness = gap_result["skill_coverage"]
                
                # Generate suggestions
                suggestions = generate_suggestions(
                    missing_skills, 
                    target_career, 
                    career_readiness
                )
        else:
            # Auto-detect best matching career
            if recommended_careers:
                target_career = recommended_careers[0]
                service = get_skill_progress_service()
                gap_result = service.analyze_skill_gap(target_career, skills)
                
                if "error" not in gap_result:
                    matching_skills = gap_result["current_skills"]
                    missing_skills = gap_result["missing_skills"]
                    career_readiness = gap_result["skill_coverage"]
                    suggestions = generate_suggestions(
                        missing_skills, 
                        target_career, 
                        career_readiness
                    )
        
        return ResumeAnalyzeResponse(
            career_readiness=career_readiness,
            detected_skills=skills,
            target_career=target_career,
            matching_skills=matching_skills,
            missing_skills=missing_skills,
            suggestions=suggestions,
            recommended_careers=recommended_careers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume-analyze-text", response_model=ResumeAnalyzeResponse)
async def analyze_resume_text(
    text: str,
    target_career: Optional[str] = None
):
    """
    Analyze resume text directly for skills and career readiness.
    
    - **text**: Resume text content
    - **target_career**: Optional target career to check readiness against
    
    Returns detected skills, career readiness, and suggestions.
    """
    if not text or len(text.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Resume text is too short"
        )
    
    try:
        # Try Groq AI first for better analysis
        if is_groq_available():
            try:
                groq = get_groq_service()
                result = groq.analyze_resume(text, target_career)
                if result:
                    return ResumeAnalyzeResponse(
                        career_readiness=result.get("career_readiness", 0),
                        detected_skills=result.get("detected_skills", []),
                        target_career=result.get("target_career"),
                        matching_skills=result.get("matching_skills", []),
                        missing_skills=result.get("missing_skills", []),
                        suggestions=result.get("suggestions", []),
                        recommended_careers=result.get("recommended_careers", [])
                    )
            except Exception as e:
                print(f"Groq API failed, falling back: {e}")
        
        # Fall back to local analysis
        analysis = analyze_resume(text)
        skills = analysis["skills"]
        recommended_careers = analysis["recommended_careers"]
        
        # Calculate career readiness if target career specified
        matching_skills = []
        missing_skills = []
        career_readiness = 0
        suggestions = []
        
        if target_career:
            service = get_skill_progress_service()
            gap_result = service.analyze_skill_gap(target_career, skills)
            
            if "error" not in gap_result:
                matching_skills = gap_result["current_skills"]
                missing_skills = gap_result["missing_skills"]
                career_readiness = gap_result["skill_coverage"]
                suggestions = generate_suggestions(
                    missing_skills, 
                    target_career, 
                    career_readiness
                )
        else:
            if recommended_careers:
                target_career = recommended_careers[0]
                service = get_skill_progress_service()
                gap_result = service.analyze_skill_gap(target_career, skills)
                
                if "error" not in gap_result:
                    matching_skills = gap_result["current_skills"]
                    missing_skills = gap_result["missing_skills"]
                    career_readiness = gap_result["skill_coverage"]
                    suggestions = generate_suggestions(
                        missing_skills, 
                        target_career, 
                        career_readiness
                    )
        
        return ResumeAnalyzeResponse(
            career_readiness=career_readiness,
            detected_skills=skills,
            target_career=target_career,
            matching_skills=matching_skills,
            missing_skills=missing_skills,
            suggestions=suggestions,
            recommended_careers=recommended_careers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_suggestions(missing_skills: list, career: str, readiness: float) -> list:
    """Generate improvement suggestions based on analysis."""
    suggestions = []
    
    if readiness < 30:
        suggestions.append(f"Focus on building foundational skills for {career}")
    elif readiness < 60:
        suggestions.append(f"You're making progress! Focus on the core missing skills")
    else:
        suggestions.append(f"Great progress! Polish your expertise in remaining areas")
    
    # Add specific skill suggestions
    if missing_skills:
        top_missing = missing_skills[:3]
        for skill in top_missing:
            suggestions.append(f"Learn {skill} through online courses or projects")
    
    # Add project suggestion
    career_data = CAREER_DATA.get(career, {})
    projects = career_data.get("projects", [])
    if projects:
        suggestions.append(f"Build a project: {projects[0]}")
    
    return suggestions
