"""
Gamification Router

Handles progress tracking, achievements, leaderboards, and XP system.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random

router = APIRouter(tags=["Gamification"])


# ==================== MODELS ====================

class DailyLog(BaseModel):
    """Daily learning log entry."""
    learned: str
    skills: List[str]
    hours: float
    mood: str
    projects: int = 0
    notes: Optional[str] = None


class DailyLogResponse(BaseModel):
    """Response for daily log submission."""
    id: str
    date: str
    learned: str
    skills: List[str]
    hours: float
    mood: str
    projects: int
    notes: Optional[str]
    xp_earned: int
    total_xp: int
    streak: int


class LeaderboardEntry(BaseModel):
    """Leaderboard entry model."""
    rank: int
    user_id: str
    name: str
    initials: str
    xp: int
    badge_count: int
    streak: int


class Achievement(BaseModel):
    """Achievement/badge model."""
    id: str
    name: str
    description: str
    icon: str
    color: str
    unlocked: bool
    unlocked_at: Optional[str] = None


class UserProgress(BaseModel):
    """User's overall progress."""
    user_id: str
    total_xp: int
    level: int
    streak: int
    weekly_xp: int
    rank: int
    badges_earned: int
    total_badges: int
    study_hours_week: float
    projects_week: int
    challenges_week: int


# ==================== IN-MEMORY STORAGE ====================

# Simulated user data storage
user_progress_data = {
    "default_user": {
        "total_xp": 1250,
        "streak": 7,
        "badges": ["first_steps", "code_master", "streak_7", "project_hero", "ml_explorer", "fast_learner", "team_player", "night_owl"],
        "daily_logs": [],
        "weekly_hours": 12,
        "weekly_projects": 1,
        "weekly_challenges": 2
    }
}

# Leaderboard data
leaderboard_data = [
    {"user_id": "alex_s", "name": "Alex Smith", "initials": "AS", "xp": 2450, "badges": 12, "streak": 14},
    {"user_id": "maya_j", "name": "Maya Johnson", "initials": "MJ", "xp": 2310, "badges": 11, "streak": 10},
    {"user_id": "raj_k", "name": "Raj Kumar", "initials": "RK", "xp": 2180, "badges": 10, "streak": 8},
    {"user_id": "sarah_l", "name": "Sarah Lee", "initials": "SL", "xp": 2050, "badges": 9, "streak": 12},
    {"user_id": "james_w", "name": "James Wilson", "initials": "JW", "xp": 1980, "badges": 9, "streak": 6},
    {"user_id": "priya_p", "name": "Priya Patel", "initials": "PP", "xp": 1850, "badges": 8, "streak": 5},
    {"user_id": "mike_c", "name": "Mike Chen", "initials": "MC", "xp": 1720, "badges": 8, "streak": 9},
    {"user_id": "emily_d", "name": "Emily Davis", "initials": "ED", "xp": 1650, "badges": 7, "streak": 4},
]

# All available achievements
all_achievements = [
    {"id": "first_steps", "name": "First Steps", "description": "Complete your first daily log", "icon": "fa-shoe-prints", "color": "from-amber-500 to-orange-500"},
    {"id": "code_master", "name": "Code Master", "description": "Practice coding for 50+ hours", "icon": "fa-code", "color": "from-emerald-500 to-teal-500"},
    {"id": "streak_7", "name": "Week Warrior", "description": "Maintain a 7-day streak", "icon": "fa-fire", "color": "from-primary-500 to-accent-500"},
    {"id": "streak_30", "name": "Monthly Master", "description": "Maintain a 30-day streak", "icon": "fa-fire-flame-curved", "color": "from-red-500 to-orange-500"},
    {"id": "project_hero", "name": "Project Hero", "description": "Complete 5 projects", "icon": "fa-trophy", "color": "from-rose-500 to-pink-500"},
    {"id": "ml_explorer", "name": "ML Explorer", "description": "Learn Machine Learning skills", "icon": "fa-brain", "color": "from-cyan-500 to-blue-500"},
    {"id": "fast_learner", "name": "Fast Learner", "description": "Earn 500 XP in one week", "icon": "fa-bolt", "color": "from-violet-500 to-purple-500"},
    {"id": "team_player", "name": "Team Player", "description": "Collaborate on team projects", "icon": "fa-users", "color": "from-lime-500 to-green-500"},
    {"id": "night_owl", "name": "Night Owl", "description": "Log activity after midnight", "icon": "fa-moon", "color": "from-indigo-500 to-blue-600"},
    {"id": "early_bird", "name": "Early Bird", "description": "Log activity before 7 AM", "icon": "fa-sun", "color": "from-yellow-400 to-orange-500"},
    {"id": "challenge_champion", "name": "Challenge Champion", "description": "Complete 10 challenges", "icon": "fa-medal", "color": "from-amber-400 to-yellow-500"},
    {"id": "skill_collector", "name": "Skill Collector", "description": "Learn 15+ different skills", "icon": "fa-gem", "color": "from-purple-500 to-pink-500"},
    {"id": "interview_ready", "name": "Interview Ready", "description": "Complete 20 interview practices", "icon": "fa-microphone", "color": "from-blue-500 to-indigo-500"},
    {"id": "top_100", "name": "Top 100", "description": "Reach top 100 on leaderboard", "icon": "fa-ranking-star", "color": "from-emerald-400 to-cyan-500"},
    {"id": "perfectionist", "name": "Perfectionist", "description": "Score 100% on any assessment", "icon": "fa-star", "color": "from-yellow-400 to-amber-500"},
    {"id": "consistency_king", "name": "Consistency King", "description": "Log for 60 consecutive days", "icon": "fa-crown", "color": "from-amber-300 to-yellow-400"},
]


# ==================== ENDPOINTS ====================

@router.post("/daily-log", response_model=DailyLogResponse)
async def submit_daily_log(log: DailyLog, user_id: str = "default_user"):
    """
    Submit a daily learning log.
    
    Calculates XP based on hours studied and projects completed.
    Updates streak and checks for achievement unlocks.
    """
    # Calculate XP
    xp_earned = int(log.hours * 15) + (log.projects * 50)
    
    # Get or create user data
    if user_id not in user_progress_data:
        user_progress_data[user_id] = {
            "total_xp": 0,
            "streak": 0,
            "badges": [],
            "daily_logs": [],
            "weekly_hours": 0,
            "weekly_projects": 0,
            "weekly_challenges": 0
        }
    
    user_data = user_progress_data[user_id]
    
    # Update user data
    user_data["total_xp"] += xp_earned
    user_data["weekly_hours"] += log.hours
    user_data["weekly_projects"] += log.projects
    
    # Update streak
    today = datetime.now().date()
    if user_data["daily_logs"]:
        last_log_date = datetime.fromisoformat(user_data["daily_logs"][-1]["date"]).date()
        if (today - last_log_date).days == 1:
            user_data["streak"] += 1
        elif (today - last_log_date).days > 1:
            user_data["streak"] = 1
    else:
        user_data["streak"] = 1
    
    # Create log entry
    log_entry = {
        "id": str(datetime.now().timestamp()),
        "date": datetime.now().isoformat(),
        "learned": log.learned,
        "skills": log.skills,
        "hours": log.hours,
        "mood": log.mood,
        "projects": log.projects,
        "notes": log.notes,
        "xp_earned": xp_earned
    }
    
    user_data["daily_logs"].append(log_entry)
    
    # Check for achievement unlocks
    check_achievements(user_id)
    
    return DailyLogResponse(
        id=log_entry["id"],
        date=log_entry["date"],
        learned=log.learned,
        skills=log.skills,
        hours=log.hours,
        mood=log.mood,
        projects=log.projects,
        notes=log.notes,
        xp_earned=xp_earned,
        total_xp=user_data["total_xp"],
        streak=user_data["streak"]
    )


@router.get("/progress/{user_id}")
async def get_user_progress(user_id: str = "default_user"):
    """
    Get user's overall progress and stats.
    """
    if user_id not in user_progress_data:
        user_progress_data[user_id] = {
            "total_xp": 0,
            "streak": 0,
            "badges": [],
            "daily_logs": [],
            "weekly_hours": 0,
            "weekly_projects": 0,
            "weekly_challenges": 0
        }
    
    user_data = user_progress_data[user_id]
    
    # Calculate level (100 XP per level)
    level = user_data["total_xp"] // 100 + 1
    
    # Calculate rank
    all_users = list(user_progress_data.values()) + leaderboard_data
    sorted_users = sorted(all_users, key=lambda x: x.get("total_xp", x.get("xp", 0)), reverse=True)
    rank = next((i + 1 for i, u in enumerate(sorted_users) if u.get("total_xp", u.get("xp", 0)) == user_data["total_xp"]), 50)
    
    return {
        "user_id": user_id,
        "total_xp": user_data["total_xp"],
        "level": level,
        "streak": user_data["streak"],
        "weekly_xp": sum(log.get("xp_earned", 0) for log in user_data["daily_logs"][-7:]),
        "rank": rank,
        "badges_earned": len(user_data["badges"]),
        "total_badges": len(all_achievements),
        "study_hours_week": user_data["weekly_hours"],
        "projects_week": user_data["weekly_projects"],
        "challenges_week": user_data["weekly_challenges"]
    }


@router.get("/daily-logs/{user_id}")
async def get_daily_logs(user_id: str = "default_user", limit: int = 10):
    """
    Get user's daily log history.
    """
    if user_id not in user_progress_data:
        return {"logs": [], "total": 0}
    
    logs = user_progress_data[user_id]["daily_logs"][-limit:]
    logs.reverse()  # Most recent first
    
    return {
        "logs": logs,
        "total": len(user_progress_data[user_id]["daily_logs"])
    }


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 50):
    """
    Get the global leaderboard.
    """
    # Combine simulated users with any real users
    all_entries = []
    
    # Add simulated leaderboard data
    for user in leaderboard_data:
        all_entries.append({
            "user_id": user["user_id"],
            "name": user["name"],
            "initials": user["initials"],
            "xp": user["xp"],
            "badge_count": user["badges"],
            "streak": user["streak"]
        })
    
    # Add real users
    for user_id, data in user_progress_data.items():
        if user_id != "default_user":
            all_entries.append({
                "user_id": user_id,
                "name": user_id.replace("_", " ").title(),
                "initials": "".join(word[0].upper() for word in user_id.split("_")[:2]),
                "xp": data["total_xp"],
                "badge_count": len(data["badges"]),
                "streak": data["streak"]
            })
    
    # Add default user
    default_data = user_progress_data.get("default_user", {"total_xp": 1250, "badges": [], "streak": 7})
    all_entries.append({
        "user_id": "default_user",
        "name": "You",
        "initials": "U",
        "xp": default_data["total_xp"],
        "badge_count": len(default_data.get("badges", [])),
        "streak": default_data.get("streak", 0),
        "is_current_user": True
    })
    
    # Sort by XP
    sorted_entries = sorted(all_entries, key=lambda x: x["xp"], reverse=True)
    
    # Add ranks
    for i, entry in enumerate(sorted_entries):
        entry["rank"] = i + 1
    
    return {
        "leaderboard": sorted_entries[:limit],
        "total_users": len(sorted_entries),
        "current_user_rank": next((e["rank"] for e in sorted_entries if e.get("is_current_user")), None)
    }


@router.get("/achievements/{user_id}")
async def get_achievements(user_id: str = "default_user"):
    """
    Get user's achievements/badges.
    """
    if user_id not in user_progress_data:
        user_badges = []
    else:
        user_badges = user_progress_data[user_id].get("badges", [])
    
    achievements = []
    for ach in all_achievements:
        achievements.append({
            **ach,
            "unlocked": ach["id"] in user_badges,
            "unlocked_at": None  # Could track unlock dates
        })
    
    return {
        "achievements": achievements,
        "unlocked_count": len(user_badges),
        "total_count": len(all_achievements)
    }


@router.get("/weekly-stats/{user_id}")
async def get_weekly_stats(user_id: str = "default_user"):
    """
    Get user's weekly statistics for charts.
    """
    if user_id not in user_progress_data:
        return {
            "daily_hours": [0, 0, 0, 0, 0, 0, 0],
            "daily_xp": [0, 0, 0, 0, 0, 0, 0],
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        }
    
    logs = user_progress_data[user_id]["daily_logs"]
    
    # Get last 7 days
    today = datetime.now().date()
    daily_hours = [0] * 7
    daily_xp = [0] * 7
    
    for log in logs:
        log_date = datetime.fromisoformat(log["date"]).date()
        days_ago = (today - log_date).days
        
        if 0 <= days_ago < 7:
            day_index = (log_date.weekday())  # 0 = Monday
            daily_hours[day_index] += log["hours"]
            daily_xp[day_index] += log.get("xp_earned", 0)
    
    return {
        "daily_hours": daily_hours,
        "daily_xp": daily_xp,
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "total_hours": sum(daily_hours),
        "total_xp": sum(daily_xp)
    }


def check_achievements(user_id: str):
    """Check and unlock achievements based on user progress."""
    if user_id not in user_progress_data:
        return
    
    user_data = user_progress_data[user_id]
    badges = user_data.get("badges", [])
    
    # First Steps - first daily log
    if len(user_data["daily_logs"]) >= 1 and "first_steps" not in badges:
        badges.append("first_steps")
    
    # Week Warrior - 7 day streak
    if user_data["streak"] >= 7 and "streak_7" not in badges:
        badges.append("streak_7")
    
    # Monthly Master - 30 day streak
    if user_data["streak"] >= 30 and "streak_30" not in badges:
        badges.append("streak_30")
    
    # Code Master - 50+ hours
    total_hours = sum(log["hours"] for log in user_data["daily_logs"])
    if total_hours >= 50 and "code_master" not in badges:
        badges.append("code_master")
    
    # Fast Learner - 500 XP in one week
    week_xp = sum(log.get("xp_earned", 0) for log in user_data["daily_logs"][-7:])
    if week_xp >= 500 and "fast_learner" not in badges:
        badges.append("fast_learner")
    
    # Project Hero - 5 projects
    total_projects = sum(log["projects"] for log in user_data["daily_logs"])
    if total_projects >= 5 and "project_hero" not in badges:
        badges.append("project_hero")
    
    user_data["badges"] = badges
