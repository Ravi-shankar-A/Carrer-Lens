"""
Run script for Career Lens application.

Usage:
    python run.py
"""

import uvicorn

if __name__ == "__main__":
    print("🎯 Starting Career Lens API...")
    print("📊 Dashboard: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"]
    )
