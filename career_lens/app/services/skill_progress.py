"""
Skill Progress Service

Provides functions for tracking and analyzing skill progress.
"""

from typing import List, Dict, Optional
from app.database.db import CAREER_DATA, get_memory_storage


class SkillProgressService:
    """Service for tracking skill progress and career readiness."""
    
    def __init__(self):
        self.storage = get_memory_storage()
    
    def calculate_progress(self, completed_skills: List[str], 
                          target_career: str) -> Dict:
        """
        Calculate skill progress towards a career.
        
        Args:
            completed_skills: List of completed skills
            target_career: Target career name
            
        Returns:
            Progress data dictionary
        """
        career_data = CAREER_DATA.get(target_career)
        
        if not career_data:
            # Try partial match
            for key in CAREER_DATA.keys():
                if target_career.lower() in key.lower() or key.lower() in target_career.lower():
                    career_data = CAREER_DATA[key]
                    target_career = key
                    break
        
        if not career_data:
            return {
                "error": "Career not found",
                "target_career": target_career
            }
        
        required_skills = career_data.get("skills", [])
        completed_lower = [s.lower() for s in completed_skills]
        
        # Calculate matching skills
        matching_skills = []
        remaining_skills = []
        
        for skill in required_skills:
            if skill.lower() in completed_lower:
                matching_skills.append(skill)
            else:
                remaining_skills.append(skill)
        
        # Calculate career readiness percentage
        total = len(required_skills)
        completed = len(matching_skills)
        
        if total > 0:
            readiness = round((completed / total) * 100, 1)
        else:
            readiness = 0
        
        return {
            "target_career": target_career,
            "completed": completed,
            "remaining": len(remaining_skills),
            "total_required": total,
            "career_readiness": readiness,
            "completed_skills": matching_skills,
            "remaining_skills": remaining_skills,
            "next_skill": remaining_skills[0] if remaining_skills else None
        }
    
    def analyze_skill_gap(self, career: str, 
                          student_skills: List[str]) -> Dict:
        """
        Analyze the skill gap between current skills and career requirements.
        
        Args:
            career: Target career
            student_skills: Current skills
            
        Returns:
            Skill gap analysis
        """
        career_data = CAREER_DATA.get(career)
        
        if not career_data:
            # Try partial match
            for key in CAREER_DATA.keys():
                if career.lower() in key.lower() or key.lower() in career.lower():
                    career_data = CAREER_DATA[key]
                    career = key
                    break
        
        if not career_data:
            return {
                "career": career,
                "error": "Career not found",
                "required_skills": [],
                "missing_skills": []
            }
        
        required_skills = career_data.get("skills", [])
        student_lower = [s.lower() for s in student_skills]
        
        # Find missing skills
        missing_skills = []
        current_skills = []
        
        for skill in required_skills:
            if skill.lower() in student_lower:
                current_skills.append(skill)
            else:
                missing_skills.append(skill)
        
        # Calculate skill coverage
        coverage = len(current_skills) / len(required_skills) * 100 if required_skills else 0
        
        return {
            "career": career,
            "required_skills": required_skills,
            "current_skills": current_skills,
            "missing_skills": missing_skills,
            "skill_coverage": round(coverage, 1)
        }
    
    def recommend_careers(self, skills: List[str]) -> Dict:
        """
        Recommend careers based on current skills.
        
        Args:
            skills: List of current skills
            
        Returns:
            Career recommendations with match scores
        """
        skills_lower = set(s.lower() for s in skills)
        recommendations = []
        
        for career, data in CAREER_DATA.items():
            required = data.get("skills", [])
            required_lower = set(s.lower() for s in required)
            
            # Calculate match
            matching = skills_lower.intersection(required_lower)
            match_count = len(matching)
            
            if required:
                match_score = (match_count / len(required)) * 100
            else:
                match_score = 0
            
            if match_count > 0:
                # Get market data
                market = data.get("market", {})
                
                recommendations.append({
                    "career": career,
                    "match_score": round(match_score, 1),
                    "matching_skills": list(matching),
                    "missing_skills": list(required_lower - skills_lower),
                    "demand": market.get("demand", "Moderate"),
                    "average_salary": market.get("average_salary", "N/A")
                })
        
        # Sort by match score
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "input_skills": skills,
            "recommended_careers": recommendations[:5]
        }
    
    def save_progress(self, user_id: str, completed_skills: List[str], 
                     target_career: str) -> Dict:
        """
        Save user progress to storage.
        
        Args:
            user_id: User identifier
            completed_skills: Completed skills
            target_career: Target career
            
        Returns:
            Saved progress data
        """
        progress_data = {
            "user_id": user_id,
            "completed_skills": completed_skills,
            "target_career": target_career
        }
        
        # Update or add to storage
        existing = None
        for i, p in enumerate(self.storage["progress"]):
            if p.get("user_id") == user_id:
                existing = i
                break
        
        if existing is not None:
            self.storage["progress"][existing] = progress_data
        else:
            self.storage["progress"].append(progress_data)
        
        # Calculate and return progress
        return self.calculate_progress(completed_skills, target_career)
    
    def get_user_progress(self, user_id: str) -> Optional[Dict]:
        """
        Get saved progress for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User's progress data or None
        """
        for p in self.storage["progress"]:
            if p.get("user_id") == user_id:
                return self.calculate_progress(
                    p["completed_skills"],
                    p["target_career"]
                )
        return None
    
    def save_daily_progress(self, user_id: str, completed_skills: List[str],
                           target_career: str, notes: str = "") -> Dict:
        """
        Save daily progress entry with timestamp.
        
        Args:
            user_id: User identifier
            completed_skills: Skills completed today
            target_career: Target career
            notes: Optional notes for the day
            
        Returns:
            Daily progress entry
        """
        from datetime import datetime
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate progress stats
        progress = self.calculate_progress(completed_skills, target_career)
        
        daily_entry = {
            "user_id": user_id,
            "date": today,
            "timestamp": datetime.now().isoformat(),
            "target_career": target_career,
            "completed_skills": completed_skills,
            "skills_count": len(completed_skills),
            "career_readiness": progress.get("career_readiness", 0),
            "remaining_count": progress.get("remaining", 0),
            "notes": notes
        }
        
        # Check if entry exists for today, update if so
        existing_idx = None
        for i, entry in enumerate(self.storage.get("daily_progress", [])):
            if entry.get("user_id") == user_id and entry.get("date") == today:
                existing_idx = i
                break
        
        if "daily_progress" not in self.storage:
            self.storage["daily_progress"] = []
        
        if existing_idx is not None:
            self.storage["daily_progress"][existing_idx] = daily_entry
        else:
            self.storage["daily_progress"].append(daily_entry)
        
        return daily_entry
    
    def get_daily_progress_history(self, user_id: str, days: int = 30) -> List[Dict]:
        """
        Get daily progress history for a user.
        
        Args:
            user_id: User identifier
            days: Number of days of history to retrieve
            
        Returns:
            List of daily progress entries
        """
        from datetime import datetime, timedelta
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        history = []
        for entry in self.storage.get("daily_progress", []):
            if entry.get("user_id") == user_id and entry.get("date", "") >= cutoff_date:
                history.append(entry)
        
        # Sort by date descending
        history.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        return history
    
    def get_progress_stats(self, user_id: str) -> Dict:
        """
        Get aggregated progress statistics.
        
        Args:
            user_id: User identifier
            
        Returns:
            Progress statistics
        """
        history = self.get_daily_progress_history(user_id, days=30)
        
        if not history:
            return {
                "total_entries": 0,
                "current_streak": 0,
                "best_streak": 0,
                "average_readiness": 0,
                "skills_growth": [],
                "readiness_trend": []
            }
        
        # Calculate streak
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        current_streak = 0
        best_streak = 0
        temp_streak = 0
        
        dates = sorted(set(e.get("date") for e in history), reverse=True)
        
        for i, date_str in enumerate(dates):
            entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            expected_date = today - timedelta(days=i)
            
            if entry_date == expected_date:
                temp_streak += 1
                current_streak = temp_streak
            else:
                best_streak = max(best_streak, temp_streak)
                temp_streak = 0
        
        best_streak = max(best_streak, temp_streak)
        
        # Calculate average readiness
        readiness_values = [e.get("career_readiness", 0) for e in history]
        avg_readiness = sum(readiness_values) / len(readiness_values) if readiness_values else 0
        
        # Readiness trend (last 7 entries)
        readiness_trend = [
            {"date": e.get("date"), "readiness": e.get("career_readiness", 0)}
            for e in history[:7]
        ]
        
        # Skills growth over time
        skills_growth = [
            {"date": e.get("date"), "count": e.get("skills_count", 0)}
            for e in history[:7]
        ]
        
        return {
            "total_entries": len(history),
            "current_streak": current_streak,
            "best_streak": best_streak,
            "average_readiness": round(avg_readiness, 1),
            "skills_growth": list(reversed(skills_growth)),
            "readiness_trend": list(reversed(readiness_trend))
        }


# Singleton instance
_service_instance = None


def get_skill_progress_service() -> SkillProgressService:
    """Get or create the skill progress service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = SkillProgressService()
    return _service_instance
