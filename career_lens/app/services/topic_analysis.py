"""
Topic Analysis Service

Provides functions for analyzing academic topics and their relevance to careers.
"""

from typing import List, Dict, Tuple, Optional
from app.database.db import CAREER_DATA, TOPIC_INDUSTRY_MAP, TOPIC_CAREER_RELEVANCE
from app.utils.nlp_utils import get_nlp_processor


class TopicAnalysisService:
    """Service for topic analysis and career relevance."""
    
    def __init__(self):
        self.nlp = get_nlp_processor()
    
    def calculate_relevance(self, topic: str, career: str) -> Dict:
        """
        Calculate the relevance between an academic topic and a career.
        
        Args:
            topic: Academic topic (e.g., "Machine Learning")
            career: Career name (e.g., "AI Engineer")
            
        Returns:
            Dictionary with relevance score and explanation
        """
        # Get career data
        career_data = CAREER_DATA.get(career)
        career_skills = career_data["skills"] if career_data else []
        
        # Calculate relevance score
        score, explanation = self.nlp.calculate_relevance_score(
            topic, career, career_skills
        )
        
        # Find related skills
        related_skills = []
        topic_lower = topic.lower()
        for skill in career_skills:
            if topic_lower in skill.lower() or skill.lower() in topic_lower:
                related_skills.append(skill)
        
        return {
            "topic": topic,
            "career": career,
            "relevance_score": score,
            "explanation": explanation,
            "related_skills": related_skills[:5]
        }
    
    def get_industry_applications(self, topic: str) -> Dict:
        """
        Get industries where a topic is applied.
        
        Args:
            topic: Academic topic
            
        Returns:
            Dictionary with industries and use cases
        """
        # Check predefined mappings
        industries = TOPIC_INDUSTRY_MAP.get(topic, [])
        
        # If no exact match, find similar topics
        if not industries:
            topic_lower = topic.lower()
            for key, value in TOPIC_INDUSTRY_MAP.items():
                if topic_lower in key.lower() or key.lower() in topic_lower:
                    industries = value
                    break
        
        # If still no match, use NLP to find relevant industries
        if not industries:
            # Default industries based on topic type
            industries = self._infer_industries(topic)
        
        # Generate use cases
        use_cases = self._generate_use_cases(topic, industries)
        
        return {
            "topic": topic,
            "industries": industries,
            "use_cases": use_cases
        }
    
    def _infer_industries(self, topic: str) -> List[str]:
        """Infer industries based on topic keywords."""
        topic_lower = topic.lower()
        
        # Keyword-based inference
        keyword_industries = {
            "data": ["Finance", "Healthcare", "E-commerce", "Marketing"],
            "machine": ["Technology", "Healthcare", "Finance", "Automotive"],
            "deep": ["Technology", "Healthcare", "Research", "Gaming"],
            "web": ["Technology", "E-commerce", "Media", "Marketing"],
            "cloud": ["Technology", "Finance", "Healthcare", "Startups"],
            "security": ["Finance", "Government", "Healthcare", "Technology"],
            "mobile": ["Technology", "E-commerce", "Entertainment", "Healthcare"],
            "database": ["Finance", "Healthcare", "E-commerce", "Technology"],
            "network": ["Telecommunications", "Technology", "Security"],
            "algorithm": ["Finance", "Technology", "Research", "Gaming"]
        }
        
        for keyword, industries in keyword_industries.items():
            if keyword in topic_lower:
                return industries
        
        # Default fallback
        return ["Technology", "Consulting", "Research"]
    
    def _generate_use_cases(self, topic: str, industries: List[str]) -> Dict[str, str]:
        """Generate use cases for topic in each industry."""
        use_case_templates = {
            "Healthcare": f"Using {topic} for medical diagnosis, patient care optimization, and drug discovery",
            "Finance": f"Applying {topic} for fraud detection, algorithmic trading, and risk assessment",
            "E-commerce": f"Leveraging {topic} for recommendation systems, customer behavior analysis",
            "Technology": f"Building innovative products and services using {topic}",
            "Autonomous Vehicles": f"Implementing {topic} for self-driving capabilities",
            "Gaming": f"Creating immersive experiences with {topic}",
            "Marketing": f"Optimizing campaigns and customer targeting with {topic}",
            "Government": f"Improving public services and decision-making with {topic}",
            "Security": f"Enhancing threat detection and prevention using {topic}",
            "Research": f"Advancing scientific discoveries through {topic}"
        }
        
        use_cases = {}
        for industry in industries:
            use_cases[industry] = use_case_templates.get(
                industry, 
                f"Applying {topic} in {industry} sector"
            )
        
        return use_cases
    
    def get_available_topics(self) -> List[str]:
        """Get list of available topics in the system."""
        return list(TOPIC_INDUSTRY_MAP.keys())
    
    def get_available_careers(self) -> List[str]:
        """Get list of available careers in the system."""
        return list(CAREER_DATA.keys())
    
    def get_topic_career_matrix(self, topics: List[str] = None, 
                                 careers: List[str] = None) -> Dict:
        """
        Generate a relevance matrix for topics and careers.
        
        Args:
            topics: List of topics (optional, uses all if None)
            careers: List of careers (optional, uses all if None)
            
        Returns:
            Matrix of relevance scores
        """
        if topics is None:
            topics = list(TOPIC_INDUSTRY_MAP.keys())[:10]
        if careers is None:
            careers = list(CAREER_DATA.keys())[:10]
        
        matrix = {}
        for topic in topics:
            matrix[topic] = {}
            for career in careers:
                result = self.calculate_relevance(topic, career)
                matrix[topic][career] = result["relevance_score"]
        
        return {
            "topics": topics,
            "careers": careers,
            "matrix": matrix
        }


# Singleton instance
_service_instance = None


def get_topic_analysis_service() -> TopicAnalysisService:
    """Get or create the topic analysis service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = TopicAnalysisService()
    return _service_instance
