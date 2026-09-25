# 🎯 Career Lens

**Academic Topic to Career Relevance Analyzer**

A full-stack platform to help students understand how academic topics relate to real-world careers and guide them toward the required skills.

![Career Lens Dashboard](https://img.shields.io/badge/Status-Working%20Prototype-green)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)

## 🚀 Features

| # | Feature | Endpoint | Description |
|---|---------|----------|-------------|
| 1 | **Topic-Career Relevance** | `POST /api/relevance` | Calculate relevance score between topics and careers |
| 2 | **Industry Applications** | `GET /api/industry-applications/{topic}` | Map topics to industries |
| 3 | **Skill Gap Analysis** | `POST /api/skill-gap` | Identify missing skills for a career |
| 4 | **Learning Path** | `GET /api/learning-path/{career}` | Get step-by-step learning roadmap |
| 5 | **Career Market Insights** | `GET /api/career-market/{career}` | View demand, salary, top companies |
| 6 | **Resume Analyzer** | `POST /api/resume-analyze` | Extract skills and assess career readiness |
| 7 | **Career Recommendations** | `POST /api/career-recommend` | Get personalized career suggestions |
| 8 | **Market Skills Analysis** | `GET /api/market-skills/{career}` | See most demanded skills |
| 9 | **Project Recommendations** | `GET /api/projects/{career}` | Get portfolio project ideas |
| 10 | **Progress Tracker** | `POST /api/progress` | Track skill progress toward career |

## 📁 Project Structure

```
career_lens/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── routers/
│   │   ├── relevance.py        # Topic-career relevance endpoints
│   │   ├── skill_gap.py        # Skill gap analysis endpoints
│   │   ├── career_recommend.py # Career recommendation endpoints
│   │   ├── resume_analyzer.py  # Resume analysis endpoints
│   │   └── projects.py         # Project & progress endpoints
│   ├── services/
│   │   ├── topic_analysis.py   # Topic relevance logic
│   │   ├── market_analysis.py  # Market insights logic
│   │   ├── learning_path.py    # Learning path generation
│   │   └── skill_progress.py   # Progress tracking logic
│   ├── models/
│   │   ├── user.py             # User models
│   │   ├── skills.py           # Skill models
│   │   └── careers.py          # Career models
│   ├── database/
│   │   └── db.py               # Database config & career data
│   └── utils/
│       └── nlp_utils.py        # NLP processing utilities
├── frontend/
│   └── dashboard.html          # Interactive dashboard
├── requirements.txt
└── README.md
```

## 🛠️ Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Quick Start

1. **Clone/Download the project**

```bash
cd career_lens
```

2. **Create a virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the application**

```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python
python -m app.main
```

5. **Access the application**

- **Dashboard**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 API Usage Examples

### 1. Topic-Career Relevance

```bash
curl -X POST "http://localhost:8000/api/relevance" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Machine Learning", "career": "AI Engineer"}'
```

**Response:**
```json
{
  "topic": "Machine Learning",
  "career": "AI Engineer",
  "relevance_score": 10,
  "explanation": "Machine Learning is the fundamental core skill for AI Engineers.",
  "related_skills": ["Deep Learning", "TensorFlow", "PyTorch"]
}
```

### 2. Industry Applications

```bash
curl "http://localhost:8000/api/industry-applications/Machine%20Learning"
```

**Response:**
```json
{
  "topic": "Machine Learning",
  "industries": ["Healthcare", "Finance", "E-commerce", "Autonomous Vehicles"],
  "use_cases": {
    "Healthcare": "Using Machine Learning for medical diagnosis and drug discovery",
    "Finance": "Applying Machine Learning for fraud detection and algorithmic trading"
  }
}
```

### 3. Skill Gap Analysis

```bash
curl -X POST "http://localhost:8000/api/skill-gap" \
  -H "Content-Type: application/json" \
  -d '{"career": "Cloud Engineer", "student_skills": ["Linux", "Networking"]}'
```

**Response:**
```json
{
  "career": "Cloud Engineer",
  "required_skills": ["Linux", "Networking", "AWS", "Docker", "Kubernetes"],
  "current_skills": ["Linux", "Networking"],
  "missing_skills": ["AWS", "Docker", "Kubernetes"],
  "skill_coverage": 40.0
}
```

### 4. Learning Path

```bash
curl "http://localhost:8000/api/learning-path/AI%20Engineer"
```

**Response:**
```json
{
  "career": "AI Engineer",
  "path": [
    "Python",
    "Mathematics & Statistics",
    "Machine Learning Fundamentals",
    "Deep Learning",
    "Specialization (NLP/CV)",
    "AI Projects & Portfolio"
  ],
  "estimated_time": "12-18 months",
  "resources": [...]
}
```

### 5. Career Market Insights

```bash
curl "http://localhost:8000/api/career-market/AI%20Engineer"
```

**Response:**
```json
{
  "career": "AI Engineer",
  "demand": "Very High",
  "average_salary": "$130,000",
  "growth_rate": "25%",
  "top_companies": ["Google", "Microsoft", "OpenAI", "Meta", "Amazon"],
  "top_skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning"]
}
```

### 6. Resume Analysis (Text)

```bash
curl -X POST "http://localhost:8000/api/resume-analyze-text?text=Experienced%20Python%20developer%20with%20Machine%20Learning%20skills&target_career=AI%20Engineer"
```

**Response:**
```json
{
  "career_readiness": 20.0,
  "detected_skills": ["Python", "Machine Learning"],
  "target_career": "AI Engineer",
  "missing_skills": ["Deep Learning", "TensorFlow", "PyTorch"],
  "suggestions": ["Learn Deep Learning through online courses"]
}
```

### 7. Career Recommendations

```bash
curl -X POST "http://localhost:8000/api/career-recommend" \
  -H "Content-Type: application/json" \
  -d '{"skills": ["Python", "SQL", "Statistics"]}'
```

**Response:**
```json
{
  "input_skills": ["Python", "SQL", "Statistics"],
  "recommended_careers": [
    {"career": "Data Scientist", "match_score": 27.3, "demand": "High"},
    {"career": "Machine Learning Engineer", "match_score": 20.0}
  ]
}
```

### 8. Project Recommendations

```bash
curl "http://localhost:8000/api/projects/AI%20Engineer"
```

**Response:**
```json
{
  "career": "AI Engineer",
  "projects": [
    "Image Classification System",
    "NLP Chatbot",
    "Recommendation Engine"
  ],
  "project_details": [...]
}
```

### 9. Progress Tracking

```bash
curl -X POST "http://localhost:8000/api/progress" \
  -H "Content-Type: application/json" \
  -d '{"completed_skills": ["Python", "Data Structures"], "target_career": "AI Engineer"}'
```

**Response:**
```json
{
  "target_career": "AI Engineer",
  "completed": 2,
  "remaining": 8,
  "career_readiness": 20.0,
  "completed_skills": ["Python"],
  "remaining_skills": ["Machine Learning", "Deep Learning", ...],
  "next_skill": "Machine Learning"
}
```

## 🖥️ Dashboard Features

The interactive dashboard includes:

- **📊 Relevance Score Gauge** - Visual gauge showing topic-career relevance
- **🏭 Industry Application Chart** - Industries where topics are used
- **📈 Skill Gap Bar Chart** - Compare required vs current skills
- **🛤️ Learning Path Timeline** - Step-by-step career roadmap
- **💼 Career Market Insights** - Demand, salary, and company data
- **📄 Resume Analysis Results** - Skills detection and suggestions
- **🎯 Career Recommendations** - Personalized career matches
- **🔧 Project Recommendations** - Portfolio project ideas
- **📊 Skill Progress Tracker** - Track learning progress

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file in the project root:

```env
# MongoDB (optional - uses in-memory storage by default)
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=career_lens

# Server
HOST=0.0.0.0
PORT=8000
```

### Optional Dependencies

The system works without these, but they enhance functionality:

- **sentence-transformers**: For semantic similarity (better relevance scoring)
- **pdfplumber**: For PDF resume parsing
- **motor**: For MongoDB persistence

## 🏗️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python, FastAPI, Pydantic, Uvicorn |
| **AI/NLP** | sentence-transformers (optional) |
| **Database** | MongoDB (optional), In-memory storage |
| **Frontend** | HTML, TailwindCSS, Chart.js |
| **File Processing** | pdfplumber, PyPDF2 |

## 📝 Supported Careers

- AI Engineer
- Data Scientist
- Machine Learning Engineer
- Cloud Engineer
- Full Stack Developer
- DevOps Engineer
- Backend Developer
- Frontend Developer
- Mobile Developer
- Cybersecurity Analyst

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

---

**Built for hackathons and educational purposes** 🎓

For questions or support, open an issue on GitHub.
