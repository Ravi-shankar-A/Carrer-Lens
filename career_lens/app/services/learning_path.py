"""
Learning Path Service

Provides functions for generating personalized learning paths and roadmaps.
"""

from typing import List, Dict, Optional
from app.database.db import CAREER_DATA


class LearningPathService:
    """Service for generating learning paths and skill roadmaps."""
    
    def get_learning_path(self, career: str) -> Dict:
        """
        Get the learning path for a specific career.
        
        Args:
            career: Career name
            
        Returns:
            Dictionary with learning path and resources
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
                "path": [],
                "estimated_time": "N/A",
                "resources": [],
                "error": "Career not found"
            }
        
        path = career_data.get("path", [])
        
        # Generate resource recommendations for each step
        resources = self._generate_resources(path)
        
        # Estimate total learning time
        estimated_time = self._estimate_time(len(path))
        
        return {
            "career": career,
            "path": path,
            "estimated_time": estimated_time,
            "resources": resources
        }
    
    def _generate_resources(self, path: List[str]) -> List[Dict]:
        """Generate learning resources for each path step."""
        resource_templates = {
            "Python": {
                "courses": ["Python for Everybody (Coursera)", "Automate the Boring Stuff"],
                "books": ["Python Crash Course", "Fluent Python"],
                "practice": "LeetCode, HackerRank"
            },
            "Statistics": {
                "courses": ["Statistics with Python (Coursera)", "Khan Academy Statistics"],
                "books": ["Think Stats", "The Elements of Statistical Learning"],
                "practice": "DataCamp exercises"
            },
            "Machine Learning": {
                "courses": ["Andrew Ng's ML Course", "Fast.ai"],
                "books": ["Hands-On Machine Learning", "Pattern Recognition"],
                "practice": "Kaggle competitions"
            },
            "Deep Learning": {
                "courses": ["Deep Learning Specialization", "Fast.ai Deep Learning"],
                "books": ["Deep Learning by Goodfellow", "Neural Networks and Deep Learning"],
                "practice": "PyTorch tutorials, TensorFlow projects"
            },
            "JavaScript": {
                "courses": ["JavaScript: Understanding the Weird Parts", "freeCodeCamp"],
                "books": ["Eloquent JavaScript", "You Don't Know JS"],
                "practice": "Frontend Mentor, JavaScript30"
            },
            "React": {
                "courses": ["React - The Complete Guide", "Epic React"],
                "books": ["React Quickly", "Learning React"],
                "practice": "Build projects, contribute to open source"
            },
            "AWS": {
                "courses": ["AWS Solutions Architect", "A Cloud Guru"],
                "books": ["AWS Certified Solutions Architect Study Guide"],
                "practice": "AWS Free Tier projects"
            },
            "Docker": {
                "courses": ["Docker for the Absolute Beginner", "Docker Deep Dive"],
                "books": ["Docker in Action", "Docker Deep Dive"],
                "practice": "Containerize personal projects"
            },
            "Kubernetes": {
                "courses": ["Kubernetes for Developers", "CKA Certification Prep"],
                "books": ["Kubernetes in Action", "The Kubernetes Book"],
                "practice": "Minikube, kind, personal clusters"
            }
        }
        
        resources = []
        for step in path:
            # Check for exact match
            if step in resource_templates:
                res = resource_templates[step]
            else:
                # Check for partial match
                matched = False
                for key, value in resource_templates.items():
                    if key.lower() in step.lower() or step.lower() in key.lower():
                        res = value
                        matched = True
                        break
                
                if not matched:
                    res = {
                        "courses": [f"Online courses for {step}"],
                        "books": [f"Books on {step}"],
                        "practice": f"Practice projects for {step}"
                    }
            
            resources.append({
                "step": step,
                "courses": res["courses"],
                "books": res["books"],
                "practice": res["practice"]
            })
        
        return resources
    
    def _estimate_time(self, num_steps: int) -> str:
        """Estimate total learning time based on path length."""
        # Assume 2-3 months per major step
        months_min = num_steps * 2
        months_max = num_steps * 3
        return f"{months_min}-{months_max} months"
    
    def get_skill_gap_path(self, career: str, current_skills: List[str]) -> Dict:
        """
        Generate a personalized learning path based on skill gaps.
        
        Args:
            career: Target career
            current_skills: Skills the user already has
            
        Returns:
            Personalized learning path
        """
        career_data = CAREER_DATA.get(career)
        
        if not career_data:
            return {"error": "Career not found"}
        
        required_skills = career_data.get("skills", [])
        current_lower = [s.lower() for s in current_skills]
        
        # Find missing skills
        missing_skills = [
            skill for skill in required_skills 
            if skill.lower() not in current_lower
        ]
        
        # Get the standard path and filter
        standard_path = career_data.get("path", [])
        
        # Create optimized path focusing on gaps
        optimized_path = []
        for step in standard_path:
            step_lower = step.lower()
            # Include step if it involves missing skills
            for skill in missing_skills:
                if skill.lower() in step_lower or step_lower in skill.lower():
                    optimized_path.append(step)
                    break
        
        # If optimized path is too short, add missing skills directly
        if len(optimized_path) < 3:
            optimized_path = missing_skills[:6]
        
        resources = self._generate_resources(optimized_path)
        
        return {
            "career": career,
            "current_skills": current_skills,
            "missing_skills": missing_skills,
            "optimized_path": optimized_path,
            "resources": resources,
            "estimated_time": self._estimate_time(len(optimized_path))
        }
    
    def get_projects_for_career(self, career: str) -> Dict:
        """
        Get recommended projects for a career.
        
        Args:
            career: Career name
            
        Returns:
            List of recommended projects with details
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
                "projects": [],
                "project_details": []
            }
        
        projects = career_data.get("projects", [])
        
        # Generate project details
        project_details = []
        difficulty_levels = ["Beginner", "Intermediate", "Intermediate", 
                           "Advanced", "Advanced", "Expert"]
        
        for i, project in enumerate(projects):
            difficulty = difficulty_levels[i] if i < len(difficulty_levels) else "Advanced"
            skills_needed = self._get_project_skills(project, career_data)
            
            project_details.append({
                "name": project,
                "difficulty": difficulty,
                "skills_needed": skills_needed,
                "estimated_hours": 20 + (i * 10),
                "description": f"Build a {project.lower()} to demonstrate your {career} skills."
            })
        
        return {
            "career": career,
            "projects": projects,
            "project_details": project_details
        }
    
    def _get_project_skills(self, project: str, career_data: Dict) -> List[str]:
        """Get relevant skills for a project."""
        all_skills = career_data.get("skills", [])
        project_lower = project.lower()
        
        # Try to match project keywords to skills
        relevant = []
        for skill in all_skills[:5]:
            relevant.append(skill)
        
        return relevant[:3]


# Singleton instance  
_service_instance = None


def get_learning_path_service() -> LearningPathService:
    """Get or create the learning path service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = LearningPathService()
    return _service_instance
