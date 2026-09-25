"""
Relevance API Router

Endpoints for topic-career relevance analysis and industry applications.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.models.careers import (
    RelevanceRequest, 
    RelevanceResponse, 
    IndustryApplicationResponse
)
from app.services.topic_analysis import get_topic_analysis_service
from app.services.groq_service import get_groq_service, is_groq_available

router = APIRouter(prefix="/api", tags=["Relevance"])


@router.post("/relevance", response_model=RelevanceResponse)
async def calculate_relevance(request: RelevanceRequest):
    """
    Calculate relevance score between an academic topic and a career.
    
    - **topic**: Academic topic (e.g., "Machine Learning", "Statistics")
    - **career**: Career name (e.g., "AI Engineer", "Data Scientist")
    
    Returns relevance score (1-10) and explanation.
    """
    # Try Groq AI first
    if is_groq_available():
        try:
            groq = get_groq_service()
            result = groq.analyze_topic_relevance(request.topic, request.career)
            if result:
                return RelevanceResponse(**result)
        except Exception as e:
            print(f"Groq API failed, falling back: {e}")
    
    # Fall back to local analysis
    service = get_topic_analysis_service()
    
    try:
        result = service.calculate_relevance(request.topic, request.career)
        return RelevanceResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/industry-applications/{topic}", response_model=IndustryApplicationResponse)
async def get_industry_applications(topic: str):
    """
    Get industries where an academic topic is applied.
    
    - **topic**: Academic topic to look up
    
    Returns list of industries and use cases.
    """
    # Try Groq AI first
    if is_groq_available():
        try:
            groq = get_groq_service()
            result = groq.get_industry_applications(topic)
            if result:
                return IndustryApplicationResponse(**result)
        except Exception as e:
            print(f"Groq API failed, falling back: {e}")
    
    # Fall back to local analysis
    service = get_topic_analysis_service()
    
    try:
        result = service.get_industry_applications(topic)
        return IndustryApplicationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics")
async def get_available_topics():
    """
    Get list of all available topics in the system.
    """
    service = get_topic_analysis_service()
    return {"topics": service.get_available_topics()}


@router.get("/careers")
async def get_available_careers():
    """
    Get list of all available careers in the system.
    """
    service = get_topic_analysis_service()
    return {"careers": service.get_available_careers()}


@router.get("/relevance-matrix")
async def get_relevance_matrix(
    topics: Optional[str] = None, 
    careers: Optional[str] = None
):
    """
    Get relevance matrix for multiple topics and careers.
    
    - **topics**: Comma-separated list of topics (optional)
    - **careers**: Comma-separated list of careers (optional)
    
    Returns matrix of relevance scores.
    """
    service = get_topic_analysis_service()
    
    topic_list = topics.split(",") if topics else None
    career_list = careers.split(",") if careers else None
    
    try:
        result = service.get_topic_career_matrix(topic_list, career_list)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
