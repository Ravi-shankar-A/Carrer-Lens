"""
Career Recommendation API Router

Endpoints for career recommendations based on skills and market insights.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.models.careers import (
    CareerRecommendRequest,
    CareerRecommendResponse,
    CareerMarketResponse,
    LearningPathResponse
)
from app.services.skill_progress import get_skill_progress_service
from app.services.market_analysis import get_market_analysis_service
from app.services.learning_path import get_learning_path_service
from app.services.groq_service import get_groq_service, is_groq_available

router = APIRouter(prefix="/api", tags=["Careers"])


@router.post("/career-recommend")
async def recommend_careers(request: CareerRecommendRequest):
    """
    Recommend careers based on the user's current skills.
    
    - **skills**: List of skills the user has
    
    Returns recommended careers with match scores.
    """
    # Try Groq AI first
    if is_groq_available():
        try:
            groq = get_groq_service()
            result = groq.recommend_careers(request.skills)
            if result:
                return result
        except Exception as e:
            print(f"Groq API failed, falling back: {e}")
    
    # Fall back to local analysis
    service = get_skill_progress_service()
    
    try:
        result = service.recommend_careers(request.skills)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/career-market/{career}", response_model=CareerMarketResponse)
async def get_career_market(career: str):
    """
    Get market insights for a specific career.
    
    - **career**: Career name
    
    Returns demand, salary, top companies, and top skills.
    """
    service = get_market_analysis_service()
    
    try:
        result = service.get_career_market_insight(career)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return CareerMarketResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning-path/{career}", response_model=LearningPathResponse)
async def get_learning_path(career: str):
    """
    Get the recommended learning path for a career.
    
    - **career**: Career name
    
    Returns step-by-step learning path with resources.
    """
    # Try Groq AI first
    if is_groq_available():
        try:
            groq = get_groq_service()
            result = groq.get_learning_path(career)
            if result:
                return LearningPathResponse(**result)
        except Exception as e:
            print(f"Groq API failed, falling back: {e}")
    
    # Fall back to local analysis
    service = get_learning_path_service()
    
    try:
        result = service.get_learning_path(career)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return LearningPathResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-careers-market")
async def get_all_careers_market():
    """
    Get market overview for all available careers.
    
    Returns list of all careers with their market data.
    """
    service = get_market_analysis_service()
    
    try:
        result = service.get_all_careers_market()
        return {"careers": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare-careers")
async def compare_careers(careers: str):
    """
    Compare multiple careers side by side.
    
    - **careers**: Comma-separated list of career names
    
    Returns comparison data for all specified careers.
    """
    service = get_market_analysis_service()
    
    career_list = [c.strip() for c in careers.split(",")]
    
    try:
        result = service.compare_careers(career_list)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/salary-comparison")
async def get_salary_comparison():
    """
    Get salary comparison across all careers.
    
    Returns careers sorted by average salary.
    """
    service = get_market_analysis_service()
    
    try:
        result = service.get_salary_comparison()
        return {"careers": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/personalized-path/{career}")
async def get_personalized_path(career: str, skills: Optional[str] = None):
    """
    Get personalized learning path based on current skills.
    
    - **career**: Target career
    - **skills**: Comma-separated list of current skills (optional)
    
    Returns optimized learning path focusing on skill gaps.
    """
    service = get_learning_path_service()
    
    skill_list = [s.strip() for s in skills.split(",")] if skills else []
    
    try:
        result = service.get_skill_gap_path(career, skill_list)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
