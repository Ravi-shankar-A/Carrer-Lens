"""
Pydantic models for Skills data.
"""

from pydantic import BaseModel
from typing import List, Optional


class Skill(BaseModel):
    """Base skill model."""
    name: str
    category: Optional[str] = None
    difficulty: Optional[str] = None  # beginner, intermediate, advanced
    description: Optional[str] = None


class SkillGapRequest(BaseModel):
    """Request model for skill gap analysis."""
    career: str
    student_skills: List[str]


class SkillGapResponse(BaseModel):
    """Response model for skill gap analysis."""
    career: str
    required_skills: List[str]
    current_skills: List[str]
    missing_skills: List[str]
    skill_coverage: float


class MarketSkillsResponse(BaseModel):
    """Response model for market skills analysis."""
    career: str
    top_skills: List[str]
    skill_demand: dict
