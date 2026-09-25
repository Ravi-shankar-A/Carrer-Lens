"""
Career Lens - Academic Topic to Career Relevance Analyzer

FastAPI application entry point.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from contextlib import asynccontextmanager
import os

# Import routers
from app.routers import relevance, skill_gap, career_recommend, resume_analyzer, projects, gamification, interview
from app.database.db import connect_to_database, close_database_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    print("🚀 Starting Career Lens API...")
    await connect_to_database()
    yield
    # Shutdown
    print("👋 Shutting down Career Lens API...")
    await close_database_connection()


# Create FastAPI application
app = FastAPI(
    title="Career Lens API",
    description="""
    **Career Lens - Academic Topic to Career Relevance Analyzer**
    
    A platform to help students understand how academic topics relate to 
    real-world careers and guide them toward the required skills.
    
    ## Features
    
    * 📊 **Topic-Career Relevance Analysis** - Calculate how relevant a topic is to a career
    * 🏭 **Industry Application Mapping** - See where topics are used in the real world
    * 📈 **Skill Gap Analysis** - Identify skills you need to learn
    * 🛤️ **Learning Path Recommendations** - Get step-by-step learning roadmaps
    * 💼 **Career Market Insights** - View job demand and salary data
    * 📄 **Resume Analysis** - Analyze your resume for career readiness
    * 🎯 **Career Recommendations** - Get personalized career suggestions
    * 🔧 **Project Recommendations** - Find projects to build your portfolio
    * 📊 **Skill Progress Tracking** - Track your learning journey
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(relevance.router)
app.include_router(skill_gap.router)
app.include_router(career_recommend.router)
app.include_router(resume_analyzer.router)
app.include_router(projects.router)
app.include_router(gamification.router, prefix="/api/gamification")
app.include_router(interview.router, prefix="/api/interview")


# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the dashboard or redirect to docs."""
    # Check if frontend file exists
    frontend_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        "frontend", 
        "dashboard.html"
    )
    
    if os.path.exists(frontend_path):
        with open(frontend_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    
    # Return a simple HTML page with links
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Career Lens API</title>
        <style>
            body {
                font-family: system-ui, -apple-system, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            h1 { font-size: 2.5rem; margin-bottom: 10px; }
            .subtitle { font-size: 1.2rem; opacity: 0.9; margin-bottom: 30px; }
            .links { display: flex; gap: 20px; flex-wrap: wrap; }
            a {
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s;
            }
            a:hover { background: rgba(255,255,255,0.3); transform: translateY(-2px); }
            .features { margin-top: 40px; }
            .feature { 
                background: rgba(255,255,255,0.1);
                padding: 15px 20px;
                border-radius: 8px;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <h1>🎯 Career Lens API</h1>
        <p class="subtitle">Academic Topic to Career Relevance Analyzer</p>
        
        <div class="links">
            <a href="/docs">📚 API Documentation</a>
            <a href="/redoc">📖 ReDoc</a>
        </div>
        
        <div class="features">
            <h2>Features</h2>
            <div class="feature">📊 Topic-Career Relevance Analysis</div>
            <div class="feature">🏭 Industry Application Mapping</div>
            <div class="feature">📈 Skill Gap Analysis</div>
            <div class="feature">🛤️ Learning Path Recommendations</div>
            <div class="feature">💼 Career Market Insights</div>
            <div class="feature">📄 Resume Analysis</div>
            <div class="feature">🎯 Career Recommendations</div>
            <div class="feature">🔧 Project Recommendations</div>
        </div>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Career Lens API",
        "version": "1.0.0"
    }


@app.get("/api/overview")
async def api_overview():
    """Get an overview of all available endpoints."""
    return {
        "name": "Career Lens API",
        "version": "1.0.0",
        "endpoints": {
            "relevance": {
                "POST /api/relevance": "Calculate topic-career relevance",
                "GET /api/industry-applications/{topic}": "Get industry applications",
                "GET /api/topics": "List available topics",
                "GET /api/careers": "List available careers"
            },
            "skills": {
                "POST /api/skill-gap": "Analyze skill gap",
                "GET /api/market-skills/{career}": "Get in-demand skills",
                "GET /api/trending-skills": "Get trending skills"
            },
            "careers": {
                "POST /api/career-recommend": "Get career recommendations",
                "GET /api/career-market/{career}": "Get market insights",
                "GET /api/learning-path/{career}": "Get learning path",
                "GET /api/all-careers-market": "Get all careers market data"
            },
            "resume": {
                "POST /api/resume-analyze": "Analyze uploaded resume (PDF)",
                "POST /api/resume-analyze-text": "Analyze resume text"
            },
            "projects": {
                "GET /api/projects/{career}": "Get project recommendations",
                "POST /api/progress": "Track skill progress",
                "GET /api/all-projects": "Get all projects"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
