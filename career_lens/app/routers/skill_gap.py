"""
Skill Gap API Router

Endpoints for skill gap analysis between student skills and career requirements.
"""

from fastapi import APIRouter, HTTPException
from typing import List

from app.models.skills import SkillGapRequest, SkillGapResponse, MarketSkillsResponse
from app.services.skill_progress import get_skill_progress_service
from app.services.market_analysis import get_market_analysis_service
from app.services.groq_service import get_groq_service, is_groq_available

router = APIRouter(prefix="/api", tags=["Skills"])


@router.post("/skill-gap", response_model=SkillGapResponse)
async def analyze_skill_gap(request: SkillGapRequest):
    """
    Analyze the skill gap between current skills and career requirements.
    
    - **career**: Target career (e.g., "Cloud Engineer")
    - **student_skills**: List of skills the student currently has
    
    Returns required skills, current skills, and missing skills.
    """
    # Try Groq AI first
    if is_groq_available():
        try:
            groq = get_groq_service()
            result = groq.analyze_skill_gap(request.career, request.student_skills)
            if result:
                return SkillGapResponse(**result)
        except Exception as e:
            print(f"Groq API failed, falling back: {e}")
    
    # Fall back to local analysis
    service = get_skill_progress_service()
    
    try:
        result = service.analyze_skill_gap(request.career, request.student_skills)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return SkillGapResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-skills/{career}", response_model=MarketSkillsResponse)
async def get_market_skills(career: str):
    """
    Get the most in-demand skills for a specific career.
    
    - **career**: Career name
    
    Returns top skills and their demand levels.
    """
    service = get_market_analysis_service()
    
    try:
        result = service.get_market_skills(career)
        return MarketSkillsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending-skills")
async def get_trending_skills(limit: int = 10):
    """
    Get the most trending skills across all careers.
    
    - **limit**: Maximum number of skills to return (default: 10)
    
    Returns list of skills with demand scores.
    """
    service = get_market_analysis_service()
    
    try:
        result = service.get_trending_skills(limit)
        return {"trending_skills": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skills-overview")
async def get_skills_overview():
    """
    Get an overview of all skills and their categories.
    """
    from app.utils.nlp_utils import SKILL_CATEGORIES
    
    return {
        "categories": SKILL_CATEGORIES,
        "total_skills": sum(len(skills) for skills in SKILL_CATEGORIES.values())
    }
