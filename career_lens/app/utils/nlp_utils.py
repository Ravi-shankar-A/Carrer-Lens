"""
NLP Utilities for Career Lens.

Provides text processing, similarity calculations, and skill extraction functions.
Uses sentence-transformers for semantic similarity when available,
falls back to keyword-based matching otherwise.
"""

import re
from typing import List, Tuple, Dict, Optional
from difflib import SequenceMatcher

# Try to import sentence-transformers for semantic similarity
try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Try to import spaCy for NLP
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


# Common programming/tech skills for extraction
KNOWN_SKILLS = [
    # Programming Languages
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "Ruby",
    "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Shell", "Bash",
    
    # Web Technologies
    "HTML", "CSS", "React", "Vue.js", "Angular", "Node.js", "Express.js", "Django",
    "Flask", "FastAPI", "Spring", "Laravel", "Ruby on Rails", "Next.js", "Svelte",
    
    # Data & ML
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Keras", "Scikit-learn",
    "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn", "NLP", "Computer Vision",
    "Neural Networks", "Reinforcement Learning", "Data Analysis", "Statistics",
    
    # Databases
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra",
    "DynamoDB", "Oracle", "SQL Server", "SQLite", "Neo4j", "GraphQL",
    
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Jenkins",
    "Terraform", "Ansible", "CI/CD", "Linux", "Git", "GitHub", "GitLab",
    "CloudFormation", "Heroku", "Vercel", "Netlify",
    
    # Other Skills
    "REST APIs", "Microservices", "System Design", "Data Structures", "Algorithms",
    "Agile", "Scrum", "JIRA", "Testing", "Unit Testing", "TDD", "API Design",
    "Networking", "Security", "Cybersecurity", "Penetration Testing", "Encryption",
    "Blockchain", "Smart Contracts", "IoT", "Embedded Systems", "Mobile Development",
    "iOS", "Android", "React Native", "Flutter", "Firebase", "Power BI", "Tableau",
    "Excel", "Data Visualization", "ETL", "Data Warehousing", "Big Data", "Spark",
    "Hadoop", "Kafka", "RabbitMQ", "Message Queues", "WebSockets", "OAuth",
    "Authentication", "Authorization", "SOLID Principles", "Design Patterns",
    "Object-Oriented Programming", "Functional Programming", "Linear Algebra",
    "Calculus", "Probability", "MLOps", "Model Deployment", "Feature Engineering",
    "A/B Testing", "Business Intelligence", "Data Mining", "Web Scraping"
]

# Skill categories for classification
SKILL_CATEGORIES = {
    "Programming Languages": ["Python", "JavaScript", "TypeScript", "Java", "C++", "C#", 
                              "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "R"],
    "Web Development": ["HTML", "CSS", "React", "Vue.js", "Angular", "Node.js", 
                        "Django", "Flask", "FastAPI", "Next.js"],
    "Data Science": ["Machine Learning", "Deep Learning", "Statistics", "Pandas", 
                     "NumPy", "Data Analysis", "Data Visualization"],
    "Cloud & DevOps": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", 
                       "Terraform", "CI/CD", "Linux"],
    "Databases": ["SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "GraphQL"],
    "Mobile": ["iOS", "Android", "React Native", "Flutter", "Swift", "Kotlin"]
}


class NLPProcessor:
    """NLP Processor for text analysis and similarity calculations."""
    
    def __init__(self):
        """Initialize NLP processor with available models."""
        self.model = None
        self.nlp = None
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize NLP models based on availability."""
        if TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("Loaded sentence-transformers model")
            except Exception as e:
                print(f"Could not load sentence-transformers: {e}")
                
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("Loaded spaCy model")
            except Exception as e:
                print(f"Could not load spaCy model: {e}")
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0 and 1
        """
        if self.model:
            # Use sentence-transformers for semantic similarity
            embeddings = self.model.encode([text1, text2], convert_to_tensor=True)
            similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
            return max(0, min(1, similarity))
        else:
            # Fallback to sequence matching
            return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract technical skills from text.
        
        Args:
            text: Text to extract skills from
            
        Returns:
            List of extracted skills
        """
        found_skills = []
        text_lower = text.lower()
        
        for skill in KNOWN_SKILLS:
            # Create variations of the skill name for matching
            variations = [
                skill.lower(),
                skill.lower().replace(".", ""),
                skill.lower().replace("-", " "),
                skill.lower().replace(" ", "")
            ]
            
            for variation in variations:
                # Check for word boundary matches
                pattern = r'\b' + re.escape(variation) + r'\b'
                if re.search(pattern, text_lower):
                    if skill not in found_skills:
                        found_skills.append(skill)
                    break
        
        return found_skills
    
    def categorize_skill(self, skill: str) -> str:
        """
        Categorize a skill into a domain.
        
        Args:
            skill: Skill name
            
        Returns:
            Category name
        """
        for category, skills in SKILL_CATEGORIES.items():
            if skill in skills:
                return category
        return "Other"
    
    def calculate_relevance_score(self, topic: str, career: str, 
                                   career_skills: List[str] = None) -> Tuple[int, str]:
        """
        Calculate relevance score between a topic and career.
        
        Args:
            topic: Academic topic
            career: Career name
            career_skills: Optional list of career skills
            
        Returns:
            Tuple of (score 1-10, explanation)
        """
        from app.database.db import TOPIC_CAREER_RELEVANCE, CAREER_DATA
        
        # Check predefined relevance data first
        key = (topic, career)
        if key in TOPIC_CAREER_RELEVANCE:
            data = TOPIC_CAREER_RELEVANCE[key]
            return data["score"], data["explanation"]
        
        # Calculate similarity-based score
        if career_skills is None:
            career_data = CAREER_DATA.get(career, {})
            career_skills = career_data.get("skills", [])
        
        # Check if topic directly matches a required skill
        topic_lower = topic.lower()
        for skill in career_skills:
            if topic_lower == skill.lower() or topic_lower in skill.lower():
                return 8, f"{topic} is directly relevant as a required skill for {career}."
        
        # Calculate semantic similarity with career description and skills
        career_text = f"{career} " + " ".join(career_skills)
        similarity = self.calculate_similarity(topic, career_text)
        
        # Convert similarity to 1-10 score
        score = min(10, max(1, int(similarity * 10) + 1))
        
        # Generate explanation
        if score >= 8:
            explanation = f"{topic} is highly relevant to {career} careers and is frequently required."
        elif score >= 6:
            explanation = f"{topic} has moderate relevance to {career} and can be beneficial."
        elif score >= 4:
            explanation = f"{topic} has some relevance to {career} but is not a core requirement."
        else:
            explanation = f"{topic} has limited direct relevance to {career} careers."
        
        return score, explanation
    
    def match_skills_to_careers(self, skills: List[str]) -> List[Tuple[str, float]]:
        """
        Match a list of skills to potential careers.
        
        Args:
            skills: List of skills
            
        Returns:
            List of (career, match_score) tuples sorted by score
        """
        from app.database.db import CAREER_DATA
        
        career_scores = []
        skill_set = set(s.lower() for s in skills)
        
        for career, data in CAREER_DATA.items():
            career_skills = set(s.lower() for s in data["skills"])
            
            # Calculate overlap
            matching = skill_set.intersection(career_skills)
            if career_skills:
                score = len(matching) / len(career_skills)
            else:
                score = 0
            
            career_scores.append((career, score, list(matching)))
        
        # Sort by score descending
        career_scores.sort(key=lambda x: x[1], reverse=True)
        return career_scores
    
    def analyze_resume_text(self, text: str) -> Dict:
        """
        Analyze resume text for skills and career fit.
        
        Args:
            text: Resume text content
            
        Returns:
            Analysis results dictionary
        """
        # Extract skills from resume
        skills = self.extract_skills(text)
        
        # Match to careers
        career_matches = self.match_skills_to_careers(skills)
        
        # Get top career recommendations
        top_careers = [c[0] for c in career_matches[:5] if c[1] > 0.1]
        
        return {
            "skills": skills,
            "career_matches": career_matches[:5],
            "recommended_careers": top_careers,
            "skill_count": len(skills)
        }


# Global NLP processor instance
nlp_processor = None


def get_nlp_processor() -> NLPProcessor:
    """Get or create the global NLP processor instance."""
    global nlp_processor
    if nlp_processor is None:
        nlp_processor = NLPProcessor()
    return nlp_processor


def extract_skills_from_text(text: str) -> List[str]:
    """Convenience function to extract skills from text."""
    return get_nlp_processor().extract_skills(text)


def calculate_topic_relevance(topic: str, career: str) -> Tuple[int, str]:
    """Convenience function to calculate topic-career relevance."""
    return get_nlp_processor().calculate_relevance_score(topic, career)


def analyze_resume(text: str) -> Dict:
    """Convenience function to analyze resume text."""
    return get_nlp_processor().analyze_resume_text(text)
