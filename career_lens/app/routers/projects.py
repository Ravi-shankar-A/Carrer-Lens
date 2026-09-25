"""
Projects API Router

Endpoints for project recommendations and skill progress tracking.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models.careers import ProjectResponse
from app.models.user import UserProgress, UserProgressResponse
from app.services.learning_path import get_learning_path_service
from app.services.skill_progress import get_skill_progress_service
from app.services.groq_service import get_groq_service, is_groq_available

router = APIRouter(prefix="/api", tags=["Projects & Progress"])


@router.get("/projects/{career}", response_model=ProjectResponse)
async def get_career_projects(career: str):
    """
    Get recommended projects for building skills in a specific career.
    
    - **career**: Career name
    
    Returns list of projects with details.
    """
    # Try Groq AI first
    if is_groq_available():
        try:
            groq = get_groq_service()
            result = groq.get_project_recommendations(career)
            if result and result.get("projects"):
                return ProjectResponse(**result)
        except Exception as e:
            print(f"Groq API failed, falling back: {e}")
    
    # Fall back to local analysis
    service = get_learning_path_service()
    
    try:
        result = service.get_projects_for_career(career)
        
        if not result.get("projects"):
            raise HTTPException(
                status_code=404, 
                detail=f"No projects found for career: {career}"
            )
        
        return ProjectResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/progress", response_model=UserProgressResponse)
async def track_progress(request: UserProgress):
    """
    Track skill progress towards a target career.
    
    - **completed_skills**: List of skills already completed
    - **target_career**: Target career to track progress against
    
    Returns progress stats and remaining skills.
    """
    service = get_skill_progress_service()
    
    try:
        result = service.calculate_progress(
            request.completed_skills, 
            request.target_career
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return UserProgressResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/progress/save")
async def save_progress(
    user_id: str,
    completed_skills: str,
    target_career: str
):
    """
    Save user progress to storage.
    
    - **user_id**: User identifier
    - **completed_skills**: Comma-separated list of completed skills
    - **target_career**: Target career
    
    Returns saved progress data.
    """
    service = get_skill_progress_service()
    
    skill_list = [s.strip() for s in completed_skills.split(",")]
    
    try:
        result = service.save_progress(user_id, skill_list, target_career)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/{user_id}")
async def get_user_progress(user_id: str):
    """
    Get saved progress for a user.
    
    - **user_id**: User identifier
    
    Returns user's progress data.
    """
    service = get_skill_progress_service()
    
    try:
        result = service.get_user_progress(user_id)
        
        if result is None:
            raise HTTPException(
                status_code=404, 
                detail=f"No progress found for user: {user_id}"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-projects")
async def get_all_projects():
    """
    Get all available projects across all careers.
    
    Returns dictionary of careers with their projects.
    """
    from app.database.db import CAREER_DATA
    
    all_projects = {}
    
    for career, data in CAREER_DATA.items():
        projects = data.get("projects", [])
        if projects:
            all_projects[career] = projects
    
    return {"projects": all_projects}


@router.get("/project-by-skill/{skill}")
async def get_projects_by_skill(skill: str):
    """
    Get projects that help develop a specific skill.
    
    - **skill**: Skill name
    
    Returns projects that utilize the specified skill.
    """
    from app.database.db import CAREER_DATA
    
    relevant_projects = []
    skill_lower = skill.lower()
    
    for career, data in CAREER_DATA.items():
        career_skills = [s.lower() for s in data.get("skills", [])]
        
        # Check if skill is relevant to this career
        if any(skill_lower in s or s in skill_lower for s in career_skills):
            projects = data.get("projects", [])
            for project in projects:
                relevant_projects.append({
                    "project": project,
                    "career": career
                })
    
    return {
        "skill": skill,
        "projects": relevant_projects[:10]
    }


# ==================== DAILY PROGRESS TRACKING ====================

@router.post("/daily-progress")
async def save_daily_progress(
    user_id: str = "default_user",
    completed_skills: str = "",
    target_career: str = "",
    notes: str = ""
):
    """
    Save daily progress entry.
    
    - **user_id**: User identifier (default: default_user)
    - **completed_skills**: Comma-separated skills completed
    - **target_career**: Target career name
    - **notes**: Optional notes for the day
    
    Returns the saved daily progress entry.
    """
    service = get_skill_progress_service()
    
    skill_list = [s.strip() for s in completed_skills.split(",") if s.strip()]
    
    try:
        result = service.save_daily_progress(user_id, skill_list, target_career, notes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily-progress/{user_id}")
async def get_daily_progress(user_id: str, days: int = 30):
    """
    Get daily progress history for a user.
    
    - **user_id**: User identifier
    - **days**: Number of days of history (default: 30)
    
    Returns list of daily progress entries.
    """
    service = get_skill_progress_service()
    
    try:
        history = service.get_daily_progress_history(user_id, days)
        return {"user_id": user_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress-stats/{user_id}")
async def get_progress_stats(user_id: str):
    """
    Get aggregated progress statistics.
    
    - **user_id**: User identifier
    
    Returns progress statistics including streaks and trends.
    """
    service = get_skill_progress_service()
    
    try:
        stats = service.get_progress_stats(user_id)
        return {"user_id": user_id, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
