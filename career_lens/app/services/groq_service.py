"""
Groq AI Service Integration

Provides AI-powered analysis using Groq's fast LLM API.
"""

import os
import json
from typing import Optional, Dict, List, Any

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"  # Fast and efficient model

# Try to import httpx for async HTTP requests
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class GroqService:
    """Service for Groq AI API interactions."""
    
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.api_url = GROQ_API_URL
        self.model = GROQ_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, messages: List[Dict], max_tokens: int = 500) -> Optional[str]:
        """Make a synchronous request to Groq API."""
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            if REQUESTS_AVAILABLE:
                import requests
                response = requests.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    print(f"Groq API error: {response.status_code} - {response.text}")
                    return None
            elif HTTPX_AVAILABLE:
                with httpx.Client() as client:
                    response = client.post(
                        self.api_url,
                        headers=self.headers,
                        json=payload,
                        timeout=30
                    )
                    if response.status_code == 200:
                        return response.json()["choices"][0]["message"]["content"]
                    return None
        except Exception as e:
            print(f"Groq API request failed: {e}")
            return None
        
        return None
    
    async def _make_async_request(self, messages: List[Dict], max_tokens: int = 500) -> Optional[str]:
        """Make an async request to Groq API."""
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            if HTTPX_AVAILABLE:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.api_url,
                        headers=self.headers,
                        json=payload,
                        timeout=30
                    )
                    if response.status_code == 200:
                        return response.json()["choices"][0]["message"]["content"]
                    else:
                        print(f"Groq API error: {response.status_code}")
                        return None
        except Exception as e:
            print(f"Groq async request failed: {e}")
            # Fall back to sync request
            return self._make_request(messages, max_tokens)
        
        return None
    
    def analyze_topic_relevance(self, topic: str, career: str) -> Dict:
        """
        Use AI to analyze topic-career relevance.
        """
        prompt = f"""Analyze the relevance of the academic topic "{topic}" to a career as a "{career}".

Provide a JSON response with:
1. relevance_score: integer from 1-10 (10 being most relevant)
2. explanation: brief 1-2 sentence explanation
3. related_skills: list of 3-5 related skills

Response format (JSON only, no markdown):
{{"relevance_score": 8, "explanation": "...", "related_skills": ["skill1", "skill2"]}}"""

        messages = [
            {"role": "system", "content": "You are a career counselor AI. Respond only with valid JSON, no markdown formatting."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=300)
        
        if response:
            try:
                # Clean response - remove markdown if present
                cleaned = response.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                cleaned = cleaned.strip()
                
                result = json.loads(cleaned)
                return {
                    "topic": topic,
                    "career": career,
                    "relevance_score": min(10, max(1, int(result.get("relevance_score", 5)))),
                    "explanation": result.get("explanation", ""),
                    "related_skills": result.get("related_skills", [])
                }
            except json.JSONDecodeError:
                pass
        
        return None
    
    def get_industry_applications(self, topic: str) -> Dict:
        """
        Use AI to identify industries where a topic is applied.
        """
        prompt = f"""List industries where "{topic}" is applied in real-world settings.

Provide a JSON response with:
1. industries: list of 5-8 industry names
2. use_cases: object mapping each industry to a brief use case description

Response format (JSON only):
{{"industries": ["Industry1", "Industry2"], "use_cases": {{"Industry1": "Use case description"}}}}"""

        messages = [
            {"role": "system", "content": "You are an industry analyst AI. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=500)
        
        if response:
            try:
                cleaned = response.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                cleaned = cleaned.strip()
                
                result = json.loads(cleaned)
                return {
                    "topic": topic,
                    "industries": result.get("industries", []),
                    "use_cases": result.get("use_cases", {})
                }
            except json.JSONDecodeError:
                pass
        
        return None
    
    def analyze_skill_gap(self, career: str, student_skills: List[str]) -> Dict:
        """
        Use AI to analyze skill gaps for a career.
        """
        skills_str = ", ".join(student_skills)
        prompt = f"""A student wants to become a "{career}" and currently has these skills: {skills_str}

Analyze the skill gap and provide a JSON response with:
1. required_skills: comprehensive list of skills needed for this career
2. missing_skills: skills the student needs to learn
3. skill_coverage: percentage of skills covered (0-100)

Response format (JSON only):
{{"required_skills": ["skill1"], "missing_skills": ["skill2"], "skill_coverage": 40}}"""

        messages = [
            {"role": "system", "content": "You are a career skills analyst AI. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=500)
        
        if response:
            try:
                cleaned = response.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                cleaned = cleaned.strip()
                
                result = json.loads(cleaned)
                return {
                    "career": career,
                    "required_skills": result.get("required_skills", []),
                    "current_skills": student_skills,
                    "missing_skills": result.get("missing_skills", []),
                    "skill_coverage": result.get("skill_coverage", 0)
                }
            except json.JSONDecodeError:
                pass
        
        return None
    
    def get_learning_path(self, career: str) -> Dict:
        """
        Use AI to generate a learning path for a career.
        """
        prompt = f"""Create a learning path roadmap for someone who wants to become a "{career}".

Provide a JSON response with:
1. path: ordered list of 6-8 learning steps/milestones
2. estimated_time: total estimated time to complete
3. resources: list of objects with step name and recommended resources

Response format (JSON only):
{{"path": ["Step 1", "Step 2"], "estimated_time": "12-18 months", "resources": [{{"step": "Step 1", "courses": ["Course"], "books": ["Book"], "practice": "Practice suggestion"}}]}}"""

        messages = [
            {"role": "system", "content": "You are a learning path designer AI. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=800)
        
        if response:
            try:
                cleaned = response.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                cleaned = cleaned.strip()
                
                result = json.loads(cleaned)
                return {
                    "career": career,
                    "path": result.get("path", []),
                    "estimated_time": result.get("estimated_time", "12-18 months"),
                    "resources": result.get("resources", [])
                }
            except json.JSONDecodeError:
                pass
        
        return None
    
    def recommend_careers(self, skills: List[str]) -> Dict:
        """
        Use AI to recommend careers based on skills.
        """
        skills_str = ", ".join(skills)
        prompt = f"""Based on these skills: {skills_str}

Recommend suitable careers and provide a JSON response with:
1. recommended_careers: list of career objects with name, match_score (0-100), and reason

Response format (JSON only):
{{"recommended_careers": [{{"career": "Career Name", "match_score": 85, "reason": "Brief reason"}}]}}"""

        messages = [
            {"role": "system", "content": "You are a career recommendation AI. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=500)
        
        if response:
            try:
                cleaned = response.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                cleaned = cleaned.strip()
                
                result = json.loads(cleaned)
                return {
                    "input_skills": skills,
                    "recommended_careers": result.get("recommended_careers", [])
                }
            except json.JSONDecodeError:
                pass
        
        return None
    
    def analyze_resume(self, resume_text: str, target_career: Optional[str] = None) -> Dict:
        """
        Use AI to analyze resume content.
        """
        career_context = f' for a "{target_career}" position' if target_career else ""
        prompt = f"""Analyze this resume{career_context}:

{resume_text[:2000]}

Provide a JSON response with:
1. detected_skills: list of technical skills found
2. career_readiness: score 0-100 for career readiness
3. missing_skills: important skills not found
4. suggestions: list of improvement suggestions
5. recommended_careers: list of suitable career paths

Response format (JSON only):
{{"detected_skills": [], "career_readiness": 50, "missing_skills": [], "suggestions": [], "recommended_careers": []}}"""

        messages = [
            {"role": "system", "content": "You are a resume analyst AI. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=600)
        
        if response:
            try:
                cleaned = response.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                cleaned = cleaned.strip()
                
                result = json.loads(cleaned)
                return {
                    "detected_skills": result.get("detected_skills", []),
                    "career_readiness": result.get("career_readiness", 0),
                    "target_career": target_career,
                    "missing_skills": result.get("missing_skills", []),
                    "suggestions": result.get("suggestions", []),
                    "recommended_careers": result.get("recommended_careers", [])
                }
            except json.JSONDecodeError:
                pass
        
        return None
    
    def get_project_recommendations(self, career: str) -> Dict:
        """
        Use AI to recommend portfolio projects.
        """
        prompt = f"""Recommend portfolio projects for someone pursuing a career as a "{career}".

Provide a JSON response with:
1. projects: list of project names
2. project_details: list of objects with name, difficulty, description, skills_needed, estimated_hours

Response format (JSON only):
{{"projects": ["Project 1"], "project_details": [{{"name": "Project 1", "difficulty": "Intermediate", "description": "...", "skills_needed": ["skill"], "estimated_hours": 20}}]}}"""

        messages = [
            {"role": "system", "content": "You are a portfolio advisor AI. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._make_request(messages, max_tokens=700)
        
        if response:
            try:
                cleaned = response.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                cleaned = cleaned.strip()
                
                result = json.loads(cleaned)
                return {
                    "career": career,
                    "projects": result.get("projects", []),
                    "project_details": result.get("project_details", [])
                }
            except json.JSONDecodeError:
                pass
        
        return None


# Singleton instance
_groq_service = None


def get_groq_service() -> GroqService:
    """Get or create the Groq service instance."""
    global _groq_service
    if _groq_service is None:
        _groq_service = GroqService()
    return _groq_service


def is_groq_available() -> bool:
    """Check if Groq API is available."""
    return bool(GROQ_API_KEY) and (HTTPX_AVAILABLE or REQUESTS_AVAILABLE)
