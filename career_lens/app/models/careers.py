"""
Pydantic models for Career data.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class CareerBase(BaseModel):
    """Base career model."""
    name: str
    description: Optional[str] = None


class Career(CareerBase):
    """Complete career model."""
    required_skills: List[str] = []
    industries: List[str] = []
    average_salary: Optional[str] = None
    demand_level: Optional[str] = None
    growth_rate: Optional[str] = None


class RelevanceRequest(BaseModel):
    """Request model for topic-career relevance."""
    topic: str
    career: str


class RelevanceResponse(BaseModel):
    """Response model for topic-career relevance."""
    topic: str
    career: str
    relevance_score: int
    explanation: str
    related_skills: Any = []


class IndustryApplicationResponse(BaseModel):
    """Response model for industry applications."""
    topic: str
    industries: List[str]
    use_cases: Dict[str, Any] = {}


class LearningPathResponse(BaseModel):
    """Response model for learning path."""
    career: str
    path: List[str]
    estimated_time: Optional[str] = None
    resources: List[Dict[str, Any]] = []


class CareerMarketResponse(BaseModel):
    """Response model for career market insights."""
    career: str
    demand: str
    average_salary: str
    growth_rate: str
    top_companies: List[str]
    top_skills: List[str]


class CareerRecommendRequest(BaseModel):
    """Request model for career recommendation."""
    skills: List[str]


class CareerRecommendResponse(BaseModel):
    """Response model for career recommendation."""
    input_skills: List[str]
    recommended_careers: List[Dict[str, Any]]


class ProjectResponse(BaseModel):
    """Response model for project recommendations."""
    career: str
    projects: List[str]
    project_details: List[Dict[str, Any]] = []


class ResumeAnalyzeResponse(BaseModel):
    """Response model for resume analysis."""
    career_readiness: float
    detected_skills: List[str]
    target_career: Optional[str] = None
    matching_skills: List[str] = []
    missing_skills: List[str] = []
    suggestions: List[str] = []
    recommended_careers: List[str] = []
