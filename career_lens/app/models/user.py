"""
Pydantic models for User data.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model."""
    name: str
    email: str
    
    
class UserCreate(UserBase):
    """Model for creating a new user."""
    target_career: Optional[str] = None
    skills: List[str] = []


class User(UserBase):
    """Complete user model with all fields."""
    id: Optional[str] = None
    target_career: Optional[str] = None
    skills: List[str] = []
    completed_skills: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class UserProgress(BaseModel):
    """Model for tracking user skill progress."""
    user_id: Optional[str] = None
    completed_skills: List[str]
    target_career: str
    
    
class UserProgressResponse(BaseModel):
    """Response model for progress tracking."""
    completed: int
    remaining: int
    career_readiness: float
    completed_skills: List[str]
    remaining_skills: List[str]
    target_career: str
    next_skill: Optional[str] = None
    total_required: Optional[int] = None
