"""
Database configuration and connection management.
Uses MongoDB for flexible document storage.
Falls back to in-memory storage if MongoDB is not available.
"""

from typing import Optional
import os
from datetime import datetime

# Try to import motor for async MongoDB, fall back to in-memory storage
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MONGODB_AVAILABLE = True
except ImportError:
    AsyncIOMotorClient = None  # type: ignore
    MONGODB_AVAILABLE = False

# Database configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "career_lens")

# Global database client
db_client = None
database = None

# In-memory fallback storage
memory_storage = {
    "users": [],
    "skills": [],
    "careers": [],
    "progress": [],
    "daily_progress": []  # Store daily progress history
}


async def connect_to_database():
    """Initialize database connection."""
    global db_client, database
    
    if MONGODB_AVAILABLE:
        try:
            db_client = AsyncIOMotorClient(MONGODB_URL)
            database = db_client[DATABASE_NAME]
            # Test connection
            await db_client.admin.command('ping')
            print(f"Connected to MongoDB at {MONGODB_URL}")
            return True
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            print("Using in-memory storage instead")
            return False
    else:
        print("Motor not installed. Using in-memory storage.")
        return False


async def close_database_connection():
    """Close database connection."""
    global db_client
    if db_client:
        db_client.close()
        print("Closed MongoDB connection")


def get_database():
    """Get database instance."""
    return database


def get_memory_storage():
    """Get in-memory storage for fallback."""
    return memory_storage


# Career data store - pre-populated with career information
CAREER_DATA = {
    "AI Engineer": {
        "skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", 
                   "NLP", "Computer Vision", "Statistics", "Linear Algebra", "Data Structures"],
        "industries": ["Technology", "Healthcare", "Finance", "Autonomous Vehicles", 
                       "E-commerce", "Gaming", "Robotics"],
        "path": ["Python", "Mathematics & Statistics", "Machine Learning Fundamentals", 
                 "Deep Learning", "Specialization (NLP/CV)", "AI Projects & Portfolio"],
        "market": {
            "demand": "Very High",
            "average_salary": "$130,000",
            "growth_rate": "25%",
            "top_companies": ["Google", "Microsoft", "OpenAI", "Meta", "Amazon", "NVIDIA"],
            "top_skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning"]
        },
        "projects": ["Image Classification System", "NLP Chatbot", "Recommendation Engine", 
                     "Object Detection Model", "Sentiment Analysis Tool", "AI-powered Search"]
    },
    "Data Scientist": {
        "skills": ["Python", "R", "SQL", "Statistics", "Machine Learning", "Data Visualization",
                   "Pandas", "NumPy", "Scikit-learn", "Tableau", "Power BI"],
        "industries": ["Finance", "Healthcare", "E-commerce", "Marketing", "Insurance", 
                       "Sports Analytics", "Government"],
        "path": ["Python/R Programming", "Statistics & Probability", "SQL & Databases",
                 "Data Wrangling", "Machine Learning", "Data Visualization", "Domain Expertise"],
        "market": {
            "demand": "High",
            "average_salary": "$120,000",
            "growth_rate": "22%",
            "top_companies": ["Google", "Meta", "Netflix", "Uber", "Airbnb", "McKinsey"],
            "top_skills": ["Python", "SQL", "Machine Learning", "Statistics", "Data Visualization"]
        },
        "projects": ["Customer Churn Prediction", "Sales Forecasting", "A/B Testing Analysis",
                     "Market Basket Analysis", "Fraud Detection", "Customer Segmentation"]
    },
    "Machine Learning Engineer": {
        "skills": ["Python", "Machine Learning", "Deep Learning", "MLOps", "Docker", 
                   "Kubernetes", "AWS/GCP", "TensorFlow", "PyTorch", "Data Engineering"],
        "industries": ["Technology", "Finance", "Healthcare", "Autonomous Systems", 
                       "Cloud Services", "Security"],
        "path": ["Python & Software Engineering", "Mathematics", "Machine Learning", 
                 "Deep Learning", "MLOps & Deployment", "Cloud Platforms"],
        "market": {
            "demand": "Very High",
            "average_salary": "$140,000",
            "growth_rate": "28%",
            "top_companies": ["Google", "Meta", "Amazon", "Apple", "Microsoft", "Tesla"],
            "top_skills": ["Python", "TensorFlow", "PyTorch", "Docker", "AWS"]
        },
        "projects": ["ML Pipeline Automation", "Model Deployment System", "Real-time Prediction API",
                     "Feature Store Implementation", "A/B Testing Framework"]
    },
    "Cloud Engineer": {
        "skills": ["Linux", "Networking", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
                   "Terraform", "CI/CD", "Python", "Bash Scripting"],
        "industries": ["Technology", "Finance", "Healthcare", "E-commerce", "Media",
                       "Government", "Startups"],
        "path": ["Linux Administration", "Networking Fundamentals", "Cloud Basics (AWS/Azure/GCP)",
                 "Containerization", "Infrastructure as Code", "Security & Compliance"],
        "market": {
            "demand": "High",
            "average_salary": "$125,000",
            "growth_rate": "20%",
            "top_companies": ["Amazon", "Microsoft", "Google", "IBM", "Salesforce", "Oracle"],
            "top_skills": ["AWS", "Docker", "Kubernetes", "Terraform", "Linux"]
        },
        "projects": ["Multi-tier Cloud Architecture", "Serverless Application", 
                     "Container Orchestration Setup", "CI/CD Pipeline", "Cloud Migration Project"]
    },
    "Full Stack Developer": {
        "skills": ["JavaScript", "TypeScript", "React", "Node.js", "Python", "SQL", 
                   "MongoDB", "HTML", "CSS", "Git", "REST APIs", "GraphQL"],
        "industries": ["Technology", "E-commerce", "Finance", "Healthcare", "Media",
                       "Education", "Startups"],
        "path": ["HTML/CSS Fundamentals", "JavaScript", "Frontend Framework (React/Vue)",
                 "Backend Development", "Database Management", "DevOps Basics"],
        "market": {
            "demand": "Very High",
            "average_salary": "$110,000",
            "growth_rate": "18%",
            "top_companies": ["Google", "Meta", "Amazon", "Netflix", "Stripe", "Shopify"],
            "top_skills": ["JavaScript", "React", "Node.js", "Python", "SQL"]
        },
        "projects": ["E-commerce Platform", "Social Media Dashboard", "Real-time Chat App",
                     "Task Management System", "Blog Platform with CMS"]
    },
    "DevOps Engineer": {
        "skills": ["Linux", "Docker", "Kubernetes", "Jenkins", "Terraform", "Ansible",
                   "AWS", "Python", "Bash", "Git", "Monitoring", "CI/CD"],
        "industries": ["Technology", "Finance", "E-commerce", "Healthcare", "Gaming",
                       "Telecommunications"],
        "path": ["Linux Administration", "Version Control", "CI/CD Fundamentals",
                 "Containerization", "Orchestration", "Infrastructure as Code", "Monitoring"],
        "market": {
            "demand": "High",
            "average_salary": "$120,000",
            "growth_rate": "21%",
            "top_companies": ["Google", "Amazon", "Netflix", "GitHub", "HashiCorp", "Datadog"],
            "top_skills": ["Docker", "Kubernetes", "AWS", "Terraform", "Jenkins"]
        },
        "projects": ["Automated Deployment Pipeline", "Infrastructure Monitoring Dashboard",
                     "Kubernetes Cluster Setup", "GitOps Workflow", "Disaster Recovery System"]
    },
    "Cybersecurity Analyst": {
        "skills": ["Network Security", "Linux", "Python", "Penetration Testing", "SIEM",
                   "Firewalls", "Encryption", "Risk Assessment", "Compliance", "Forensics"],
        "industries": ["Finance", "Government", "Healthcare", "Technology", "Defense",
                       "Consulting"],
        "path": ["Networking Fundamentals", "Operating Systems", "Security Fundamentals",
                 "Ethical Hacking", "Security Tools", "Compliance & Governance"],
        "market": {
            "demand": "Very High",
            "average_salary": "$105,000",
            "growth_rate": "32%",
            "top_companies": ["Palo Alto", "CrowdStrike", "IBM", "Cisco", "Microsoft", "Deloitte"],
            "top_skills": ["Network Security", "SIEM", "Penetration Testing", "Python", "Linux"]
        },
        "projects": ["Vulnerability Assessment Tool", "SIEM Dashboard", "Penetration Test Report",
                     "Security Audit Framework", "Incident Response Plan"]
    },
    "Backend Developer": {
        "skills": ["Python", "Java", "Node.js", "SQL", "MongoDB", "Redis", "Docker",
                   "REST APIs", "GraphQL", "Microservices", "Message Queues"],
        "industries": ["Technology", "Finance", "E-commerce", "Healthcare", "Media",
                       "Gaming"],
        "path": ["Programming Fundamentals", "Data Structures", "Database Design",
                 "API Development", "System Design", "Performance Optimization"],
        "market": {
            "demand": "High",
            "average_salary": "$115,000",
            "growth_rate": "17%",
            "top_companies": ["Google", "Amazon", "Stripe", "Twilio", "MongoDB", "Uber"],
            "top_skills": ["Python", "Java", "SQL", "Docker", "REST APIs"]
        },
        "projects": ["RESTful API Service", "Microservices Architecture", "Payment Gateway",
                     "Authentication System", "Real-time Data Pipeline"]
    },
    "Frontend Developer": {
        "skills": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Vue.js", "Angular",
                   "Responsive Design", "Web Performance", "Testing", "Git"],
        "industries": ["Technology", "E-commerce", "Media", "Marketing", "Education",
                       "Entertainment"],
        "path": ["HTML & CSS", "JavaScript Fundamentals", "Responsive Design",
                 "Frontend Framework", "State Management", "Testing & Optimization"],
        "market": {
            "demand": "High",
            "average_salary": "$100,000",
            "growth_rate": "15%",
            "top_companies": ["Google", "Meta", "Airbnb", "Spotify", "Figma", "Vercel"],
            "top_skills": ["JavaScript", "React", "TypeScript", "CSS", "HTML"]
        },
        "projects": ["Portfolio Website", "Interactive Dashboard", "E-commerce UI",
                     "Component Library", "Progressive Web App"]
    },
    "Mobile Developer": {
        "skills": ["Swift", "Kotlin", "React Native", "Flutter", "iOS", "Android",
                   "Mobile UI/UX", "REST APIs", "Firebase", "App Store Deployment"],
        "industries": ["Technology", "E-commerce", "Healthcare", "Finance", "Entertainment",
                       "Social Media"],
        "path": ["Programming Fundamentals", "Platform Basics (iOS/Android)", "UI Development",
                 "API Integration", "State Management", "App Deployment"],
        "market": {
            "demand": "High",
            "average_salary": "$115,000",
            "growth_rate": "19%",
            "top_companies": ["Apple", "Google", "Meta", "Uber", "Spotify", "TikTok"],
            "top_skills": ["Swift", "Kotlin", "React Native", "Flutter", "Firebase"]
        },
        "projects": ["Social Media App", "Fitness Tracker", "Food Delivery App",
                     "Finance Management App", "E-commerce Mobile App"]
    }
}


# Topic to industry mapping
TOPIC_INDUSTRY_MAP = {
    "Machine Learning": ["Healthcare", "Finance", "E-commerce", "Autonomous Vehicles", 
                         "Technology", "Gaming", "Insurance", "Marketing"],
    "Deep Learning": ["Healthcare", "Autonomous Vehicles", "Gaming", "Technology",
                      "Security", "Research"],
    "Natural Language Processing": ["Technology", "Customer Service", "Healthcare", 
                                     "Legal", "Media", "Education"],
    "Computer Vision": ["Autonomous Vehicles", "Healthcare", "Security", "Retail",
                        "Manufacturing", "Entertainment"],
    "Data Analysis": ["Finance", "Healthcare", "Marketing", "E-commerce", "Sports",
                      "Government", "Consulting"],
    "Cloud Computing": ["Technology", "Finance", "Healthcare", "E-commerce", "Media",
                        "Government", "Startups"],
    "Cybersecurity": ["Finance", "Government", "Healthcare", "Technology", "Defense",
                      "Consulting"],
    "Web Development": ["Technology", "E-commerce", "Media", "Education", "Finance",
                        "Healthcare"],
    "Mobile Development": ["Technology", "E-commerce", "Healthcare", "Finance",
                           "Entertainment", "Social Media"],
    "Database Management": ["Finance", "Healthcare", "E-commerce", "Technology",
                            "Government", "Consulting"],
    "DevOps": ["Technology", "Finance", "E-commerce", "Healthcare", "Gaming",
               "Telecommunications"],
    "Blockchain": ["Finance", "Supply Chain", "Healthcare", "Government", "Real Estate"],
    "Python": ["Data Science", "AI/ML", "Web Development", "Automation", "Finance"],
    "JavaScript": ["Web Development", "Mobile Apps", "Enterprise Software", "Gaming"],
    "Statistics": ["Data Science", "Finance", "Healthcare", "Research", "Marketing"],
    "Data Structures": ["Software Development", "System Design", "All Tech Industries"],
    "Algorithms": ["Software Development", "Finance", "Gaming", "Research"],
    "Networking": ["Telecommunications", "Cloud Computing", "Security", "Technology"],
    "Linux": ["Cloud Computing", "DevOps", "Security", "Technology", "Research"],
    "SQL": ["Data Analysis", "Web Development", "Enterprise", "Finance", "Healthcare"]
}


# Topic relevance to careers
TOPIC_CAREER_RELEVANCE = {
    ("Machine Learning", "AI Engineer"): {
        "score": 10,
        "explanation": "Machine Learning is the fundamental core skill for AI Engineers. It's essential for building intelligent systems."
    },
    ("Machine Learning", "Data Scientist"): {
        "score": 9,
        "explanation": "Machine Learning is crucial for Data Scientists to build predictive models and extract insights from data."
    },
    ("Machine Learning", "Machine Learning Engineer"): {
        "score": 10,
        "explanation": "This is the defining skill for ML Engineers who specialize in deploying ML models at scale."
    },
    ("Deep Learning", "AI Engineer"): {
        "score": 9,
        "explanation": "Deep Learning powers modern AI applications like computer vision and NLP that AI Engineers build."
    },
    ("Python", "AI Engineer"): {
        "score": 9,
        "explanation": "Python is the primary programming language for AI development with rich ML/DL library ecosystem."
    },
    ("Python", "Data Scientist"): {
        "score": 9,
        "explanation": "Python is the most popular language for data science with pandas, numpy, and visualization libraries."
    },
    ("Python", "Backend Developer"): {
        "score": 8,
        "explanation": "Python is widely used for backend development with frameworks like Django and FastAPI."
    },
    ("Statistics", "Data Scientist"): {
        "score": 10,
        "explanation": "Statistics is foundational for data science, used in hypothesis testing, modeling, and inference."
    },
    ("Cloud Computing", "Cloud Engineer"): {
        "score": 10,
        "explanation": "Cloud Computing is the core domain for Cloud Engineers who design and manage cloud infrastructure."
    },
    ("Docker", "DevOps Engineer"): {
        "score": 9,
        "explanation": "Docker containerization is essential for DevOps practices in modern software deployment."
    },
    ("Kubernetes", "DevOps Engineer"): {
        "score": 9,
        "explanation": "Kubernetes orchestration is critical for managing containerized applications at scale."
    },
    ("JavaScript", "Full Stack Developer"): {
        "score": 10,
        "explanation": "JavaScript is essential for both frontend and backend (Node.js) in full stack development."
    },
    ("JavaScript", "Frontend Developer"): {
        "score": 10,
        "explanation": "JavaScript is the core language for frontend web development and interactivity."
    },
    ("React", "Frontend Developer"): {
        "score": 9,
        "explanation": "React is the most popular frontend framework used in modern web development."
    },
    ("SQL", "Data Scientist"): {
        "score": 8,
        "explanation": "SQL is essential for data extraction and manipulation in data science workflows."
    },
    ("SQL", "Backend Developer"): {
        "score": 8,
        "explanation": "SQL is crucial for database operations in backend development."
    },
    ("Networking", "Cloud Engineer"): {
        "score": 8,
        "explanation": "Networking knowledge is essential for designing and managing cloud network architectures."
    },
    ("Networking", "Cybersecurity Analyst"): {
        "score": 9,
        "explanation": "Network security fundamentals are core to cybersecurity analysis and defense."
    },
    ("Linux", "DevOps Engineer"): {
        "score": 9,
        "explanation": "Linux is the dominant OS for servers and essential for DevOps operations."
    },
    ("Linux", "Cloud Engineer"): {
        "score": 8,
        "explanation": "Most cloud infrastructure runs on Linux, making it essential for cloud engineers."
    }
}
