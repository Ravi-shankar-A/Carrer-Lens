"""
Interview Prep Router

Handles interview questions, practice sessions, and mock interviews.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import random
import os

router = APIRouter(tags=["Interview Prep"])


# ==================== MODELS ====================

class InterviewQuestion(BaseModel):
    """Interview question model."""
    id: str
    category: str  # "technical", "behavioral", "company"
    subcategory: str  # "dsa", "system_design", "coding", "star", "leadership", etc.
    difficulty: str  # "easy", "medium", "hard"
    question: str
    hints: Optional[List[str]] = None
    sample_answer: Optional[str] = None
    follow_ups: Optional[List[str]] = None
    company: Optional[str] = None


class PracticeSessionRequest(BaseModel):
    """Request for starting a practice session."""
    category: str
    subcategory: Optional[str] = None
    difficulty: Optional[str] = None
    num_questions: int = 5


class PracticeResponse(BaseModel):
    """User's response to a practice question."""
    question_id: str
    answer: str
    time_taken_seconds: int


class MockInterviewRequest(BaseModel):
    """Request for a mock interview session."""
    company: Optional[str] = None
    role: str
    duration_minutes: int = 30
    include_technical: bool = True
    include_behavioral: bool = True


# ==================== QUESTION BANKS ====================

# DSA Questions
dsa_questions = [
    {
        "id": "dsa_1",
        "question": "Explain the difference between an array and a linked list. When would you use each?",
        "hints": ["Consider memory allocation", "Think about insertion/deletion complexity", "Random access"],
        "sample_answer": "Arrays provide O(1) random access but O(n) insertion/deletion. Linked lists offer O(1) insertion/deletion at known positions but O(n) access. Use arrays for frequent access, linked lists for frequent modifications.",
        "difficulty": "easy"
    },
    {
        "id": "dsa_2",
        "question": "Implement a function to detect if a linked list has a cycle.",
        "hints": ["Floyd's cycle detection", "Two pointers: slow and fast", "O(1) space complexity"],
        "sample_answer": "Use Floyd's tortoise and hare algorithm. Move slow pointer by 1 and fast by 2. If they meet, there's a cycle.",
        "difficulty": "medium"
    },
    {
        "id": "dsa_3",
        "question": "Design an LRU Cache with O(1) get and put operations.",
        "hints": ["Combine hash map and linked list", "Doubly linked list for O(1) removal", "Track most/least recently used"],
        "sample_answer": "Use a hash map for O(1) lookup and a doubly linked list to maintain order. Move accessed items to front, evict from back.",
        "difficulty": "hard"
    },
    {
        "id": "dsa_4",
        "question": "What is the time complexity of binary search? When can it be applied?",
        "hints": ["Think about sorted data", "Divide and conquer", "Compare with linear search"],
        "sample_answer": "O(log n) time complexity. Can only be applied to sorted arrays/collections. Each comparison eliminates half the remaining elements.",
        "difficulty": "easy"
    },
    {
        "id": "dsa_5",
        "question": "Explain how a hash table works and discuss collision resolution strategies.",
        "hints": ["Hash function maps keys to indices", "Chaining vs open addressing", "Load factor"],
        "sample_answer": "Hash tables use a hash function to map keys to array indices. Collisions are handled via chaining (linked lists at each index) or open addressing (probing for next empty slot).",
        "difficulty": "medium"
    }
]

# System Design Questions
system_design_questions = [
    {
        "id": "sd_1",
        "question": "Design a URL shortening service like bit.ly.",
        "hints": ["Consider unique ID generation", "Database schema", "Redirection mechanism", "Analytics"],
        "difficulty": "medium"
    },
    {
        "id": "sd_2",
        "question": "Design a distributed cache system like Redis.",
        "hints": ["Caching strategies (LRU, LFU)", "Sharding", "Replication", "Consistency vs Availability"],
        "difficulty": "hard"
    },
    {
        "id": "sd_3",
        "question": "Design a real-time chat application like WhatsApp.",
        "hints": ["WebSocket connections", "Message queues", "Presence detection", "Group messaging"],
        "difficulty": "hard"
    },
    {
        "id": "sd_4",
        "question": "Design a rate limiter for an API.",
        "hints": ["Token bucket algorithm", "Sliding window", "Distributed rate limiting", "Redis"],
        "difficulty": "medium"
    },
    {
        "id": "sd_5",
        "question": "Design a news feed system like Facebook's.",
        "hints": ["Fan-out on write vs read", "Caching", "Ranking algorithm", "Real-time updates"],
        "difficulty": "hard"
    }
]

# Coding Questions
coding_questions = [
    {
        "id": "code_1",
        "question": "Write a function to find the first non-repeating character in a string.",
        "hints": ["Use hash map to count occurrences", "Second pass to find first with count 1"],
        "difficulty": "easy"
    },
    {
        "id": "code_2",
        "question": "Implement a function to merge two sorted arrays without extra space.",
        "hints": ["Start from the end", "Use the available space in first array", "Two pointers"],
        "difficulty": "medium"
    },
    {
        "id": "code_3",
        "question": "Write a function to find all permutations of a string.",
        "hints": ["Backtracking", "Swap characters", "Recursion"],
        "difficulty": "medium"
    },
    {
        "id": "code_4",
        "question": "Implement a function to find the longest palindromic substring.",
        "hints": ["Expand around center", "Dynamic programming", "O(n²) possible"],
        "difficulty": "medium"
    },
    {
        "id": "code_5",
        "question": "Write a function to serialize and deserialize a binary tree.",
        "hints": ["BFS or DFS traversal", "Handle null nodes", "Delimiters"],
        "difficulty": "hard"
    }
]

# Behavioral Questions - STAR Method
behavioral_star_questions = [
    {
        "id": "star_1",
        "question": "Tell me about a time when you had to meet a tight deadline. How did you handle it?",
        "hints": ["Use STAR format", "Focus on your specific actions", "Quantify results if possible"],
        "difficulty": "medium"
    },
    {
        "id": "star_2",
        "question": "Describe a situation where you had to deal with a difficult team member.",
        "hints": ["Focus on resolution", "Show empathy", "Highlight communication skills"],
        "difficulty": "medium"
    },
    {
        "id": "star_3",
        "question": "Tell me about a time you failed. What did you learn?",
        "hints": ["Be honest", "Show growth mindset", "Focus on lessons learned"],
        "difficulty": "medium"
    },
    {
        "id": "star_4",
        "question": "Describe a project you're most proud of and your role in it.",
        "hints": ["Highlight your contributions", "Show impact", "Demonstrate technical skills"],
        "difficulty": "easy"
    },
    {
        "id": "star_5",
        "question": "Tell me about a time when you had to learn something new quickly.",
        "hints": ["Show adaptability", "Describe your learning process", "Result achieved"],
        "difficulty": "easy"
    }
]

# Leadership Questions
leadership_questions = [
    {
        "id": "lead_1",
        "question": "Describe a time when you took initiative without being asked.",
        "hints": ["Show proactivity", "Impact of your action", "How others responded"],
        "difficulty": "medium"
    },
    {
        "id": "lead_2",
        "question": "How do you motivate team members who are underperforming?",
        "hints": ["Empathy first", "Identify root causes", "Create action plan"],
        "difficulty": "hard"
    },
    {
        "id": "lead_3",
        "question": "Tell me about a time you had to make a difficult decision with incomplete information.",
        "hints": ["Decision-making process", "Risk assessment", "Outcome and learnings"],
        "difficulty": "hard"
    }
]

# Teamwork Questions
teamwork_questions = [
    {
        "id": "team_1",
        "question": "How do you handle disagreements with teammates about technical decisions?",
        "hints": ["Data-driven discussion", "Finding compromise", "Respecting diverse opinions"],
        "difficulty": "medium"
    },
    {
        "id": "team_2",
        "question": "Describe your ideal team environment. How do you contribute to it?",
        "hints": ["Culture fit", "Your values", "Concrete examples"],
        "difficulty": "easy"
    },
    {
        "id": "team_3",
        "question": "Tell me about a successful collaboration with someone from a different team or department.",
        "hints": ["Cross-functional work", "Communication", "Shared goals"],
        "difficulty": "medium"
    }
]

# Company-specific questions
company_questions = {
    "Google": [
        {
            "id": "google_1",
            "question": "Why do you want to work at Google specifically?",
            "hints": ["Research Google's mission", "Align with your values", "Specific products/teams"],
            "difficulty": "easy"
        },
        {
            "id": "google_2",
            "question": "How do you approach ambiguity in projects?",
            "hints": ["Google values this", "Show structured thinking", "Example of navigating ambiguity"],
            "difficulty": "medium"
        },
        {
            "id": "google_3",
            "question": "Describe a time you used data to make a decision.",
            "hints": ["Data-driven culture", "Analytics mindset", "Metrics and outcomes"],
            "difficulty": "medium"
        }
    ],
    "Microsoft": [
        {
            "id": "ms_1",
            "question": "What Microsoft product would you improve and how?",
            "hints": ["Research current products", "User-centric thinking", "Technical feasibility"],
            "difficulty": "medium"
        },
        {
            "id": "ms_2",
            "question": "How do you balance innovation with reliability in software?",
            "hints": ["Enterprise focus", "Testing strategies", "Incremental improvement"],
            "difficulty": "medium"
        },
        {
            "id": "ms_3",
            "question": "Describe your experience with cloud technologies.",
            "hints": ["Azure knowledge", "Cloud architecture", "Scalability concepts"],
            "difficulty": "medium"
        }
    ],
    "Amazon": [
        {
            "id": "amz_1",
            "question": "Tell me about a time you were customer-obsessed.",
            "hints": ["Amazon Leadership Principle", "Customer impact", "Going above and beyond"],
            "difficulty": "medium"
        },
        {
            "id": "amz_2",
            "question": "Describe a situation where you had to dive deep to solve a problem.",
            "hints": ["Another Leadership Principle", "Root cause analysis", "Technical depth"],
            "difficulty": "medium"
        },
        {
            "id": "amz_3",
            "question": "How do you prioritize when everything seems urgent?",
            "hints": ["Bias for action", "Impact vs effort", "Communication"],
            "difficulty": "medium"
        }
    ],
    "Meta": [
        {
            "id": "meta_1",
            "question": "What would you build if you had unlimited resources at Meta?",
            "hints": ["Innovation mindset", "Social impact", "Technical vision"],
            "difficulty": "medium"
        },
        {
            "id": "meta_2",
            "question": "How do you approach building products for billions of users?",
            "hints": ["Scale considerations", "Diverse user base", "Performance"],
            "difficulty": "hard"
        },
        {
            "id": "meta_3",
            "question": "Describe your experience with large-scale distributed systems.",
            "hints": ["Technical depth", "Real examples", "Challenges overcome"],
            "difficulty": "hard"
        }
    ]
}


# ==================== IN-MEMORY STORAGE ====================

practice_sessions = {}
interview_stats = {
    "default_user": {
        "questions_practiced": 45,
        "hours_practiced": 12,
        "mock_interviews": 3,
        "strong_areas": ["behavioral", "coding"],
        "weak_areas": ["system_design"]
    }
}


# ==================== ENDPOINTS ====================

@router.get("/questions/{category}")
async def get_questions(
    category: str,
    subcategory: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 10
):
    """
    Get interview questions by category.
    
    Categories: technical, behavioral, company
    Subcategories: 
      - Technical: dsa, system_design, coding
      - Behavioral: star, leadership, teamwork
      - Company: google, microsoft, amazon, meta
    """
    questions = []
    
    if category == "technical":
        if subcategory == "dsa" or subcategory is None:
            questions.extend(dsa_questions)
        if subcategory == "system_design" or subcategory is None:
            questions.extend(system_design_questions)
        if subcategory == "coding" or subcategory is None:
            questions.extend(coding_questions)
    
    elif category == "behavioral":
        if subcategory == "star" or subcategory is None:
            questions.extend(behavioral_star_questions)
        if subcategory == "leadership" or subcategory is None:
            questions.extend(leadership_questions)
        if subcategory == "teamwork" or subcategory is None:
            questions.extend(teamwork_questions)
    
    elif category == "company":
        if subcategory and subcategory.title() in company_questions:
            questions.extend(company_questions[subcategory.title()])
        elif subcategory is None:
            for co_questions in company_questions.values():
                questions.extend(co_questions)
    
    # Filter by difficulty
    if difficulty:
        questions = [q for q in questions if q.get("difficulty") == difficulty]
    
    # Format for response
    formatted = []
    for q in questions[:limit]:
        formatted.append(InterviewQuestion(
            id=q["id"],
            category=category,
            subcategory=subcategory or "mixed",
            difficulty=q.get("difficulty", "medium"),
            question=q["question"],
            hints=q.get("hints"),
            sample_answer=q.get("sample_answer"),
            follow_ups=q.get("follow_ups"),
            company=q.get("company")
        ))
    
    return {"questions": formatted, "total": len(formatted)}


@router.post("/practice/start")
async def start_practice_session(request: PracticeSessionRequest, user_id: str = "default_user"):
    """
    Start a new practice session.
    """
    # Get questions based on request
    questions_response = await get_questions(
        category=request.category,
        subcategory=request.subcategory,
        difficulty=request.difficulty,
        limit=request.num_questions
    )
    
    session_id = f"session_{datetime.now().timestamp()}"
    
    # Shuffle questions
    questions = questions_response["questions"]
    random.shuffle(questions)
    
    practice_sessions[session_id] = {
        "user_id": user_id,
        "questions": [q.model_dump() for q in questions],
        "responses": [],
        "started_at": datetime.now().isoformat(),
        "current_index": 0
    }
    
    return {
        "session_id": session_id,
        "total_questions": len(questions),
        "first_question": questions[0] if questions else None
    }


@router.post("/practice/{session_id}/answer")
async def submit_practice_answer(session_id: str, response: PracticeResponse):
    """
    Submit an answer for a practice question.
    """
    if session_id not in practice_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = practice_sessions[session_id]
    session["responses"].append(response.model_dump())
    session["current_index"] += 1
    
    # Get next question
    if session["current_index"] < len(session["questions"]):
        next_question = session["questions"][session["current_index"]]
    else:
        next_question = None
    
    # Get current question for feedback
    current_q = next((q for q in session["questions"] if q["id"] == response.question_id), None)
    
    return {
        "recorded": True,
        "sample_answer": current_q.get("sample_answer") if current_q else None,
        "next_question": next_question,
        "progress": f"{session['current_index']}/{len(session['questions'])}"
    }


@router.get("/practice/{session_id}/complete")
async def complete_practice_session(session_id: str):
    """
    Complete a practice session and get summary.
    """
    if session_id not in practice_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = practice_sessions[session_id]
    
    # Calculate stats
    total_time = sum(r.get("time_taken_seconds", 0) for r in session["responses"])
    questions_answered = len(session["responses"])
    
    # Update user stats
    user_id = session["user_id"]
    if user_id in interview_stats:
        interview_stats[user_id]["questions_practiced"] += questions_answered
        interview_stats[user_id]["hours_practiced"] += total_time / 3600
    
    return {
        "session_id": session_id,
        "questions_answered": questions_answered,
        "total_questions": len(session["questions"]),
        "total_time_seconds": total_time,
        "average_time_per_question": total_time / max(questions_answered, 1),
        "completed_at": datetime.now().isoformat()
    }


@router.post("/mock-interview/start")
async def start_mock_interview(request: MockInterviewRequest, user_id: str = "default_user"):
    """
    Start an AI-powered mock interview session.
    """
    questions = []
    
    # Add technical questions
    if request.include_technical:
        tech_questions = random.sample(dsa_questions + coding_questions, min(3, len(dsa_questions)))
        questions.extend(tech_questions)
    
    # Add behavioral questions
    if request.include_behavioral:
        behav_questions = random.sample(behavioral_star_questions, min(2, len(behavioral_star_questions)))
        questions.extend(behav_questions)
    
    # Add company-specific questions
    if request.company and request.company.title() in company_questions:
        company_qs = random.sample(
            company_questions[request.company.title()], 
            min(2, len(company_questions[request.company.title()]))
        )
        questions.extend(company_qs)
    
    # Shuffle
    random.shuffle(questions)
    
    session_id = f"mock_{datetime.now().timestamp()}"
    
    practice_sessions[session_id] = {
        "type": "mock_interview",
        "user_id": user_id,
        "company": request.company,
        "role": request.role,
        "questions": questions,
        "responses": [],
        "started_at": datetime.now().isoformat(),
        "duration_minutes": request.duration_minutes,
        "current_index": 0
    }
    
    return {
        "session_id": session_id,
        "interview_type": "mock",
        "company": request.company,
        "role": request.role,
        "total_questions": len(questions),
        "duration_minutes": request.duration_minutes,
        "first_question": {
            "question": questions[0]["question"] if questions else None,
            "hints": questions[0].get("hints") if questions else None
        },
        "intro_message": f"Welcome to your mock interview for {request.role} position" + 
                        (f" at {request.company}" if request.company else "") + 
                        ". Take your time to think through each question. Good luck!"
    }


@router.get("/stats/{user_id}")
async def get_interview_stats(user_id: str = "default_user"):
    """
    Get user's interview preparation statistics.
    """
    if user_id not in interview_stats:
        interview_stats[user_id] = {
            "questions_practiced": 0,
            "hours_practiced": 0,
            "mock_interviews": 0,
            "strong_areas": [],
            "weak_areas": []
        }
    
    stats = interview_stats[user_id]
    
    return {
        "user_id": user_id,
        "questions_practiced": stats["questions_practiced"],
        "hours_practiced": round(stats["hours_practiced"], 1),
        "mock_interviews": stats["mock_interviews"],
        "strong_areas": stats["strong_areas"],
        "weak_areas": stats["weak_areas"],
        "readiness_score": min(100, stats["questions_practiced"] * 2 + stats["mock_interviews"] * 10)
    }


@router.get("/companies")
async def get_supported_companies():
    """
    Get list of companies with specific interview prep content.
    """
    return {
        "companies": [
            {
                "id": "google",
                "name": "Google",
                "logo": "https://logo.clearbit.com/google.com",
                "focus_areas": ["Algorithms", "System Design", "Leadership"],
                "question_count": len(company_questions.get("Google", []))
            },
            {
                "id": "microsoft",
                "name": "Microsoft",
                "logo": "https://logo.clearbit.com/microsoft.com",
                "focus_areas": ["Cloud", "Enterprise", "Innovation"],
                "question_count": len(company_questions.get("Microsoft", []))
            },
            {
                "id": "amazon",
                "name": "Amazon",
                "logo": "https://logo.clearbit.com/amazon.com",
                "focus_areas": ["Leadership Principles", "System Design", "Data"],
                "question_count": len(company_questions.get("Amazon", []))
            },
            {
                "id": "meta",
                "name": "Meta",
                "logo": "https://logo.clearbit.com/meta.com",
                "focus_areas": ["Scale", "Social Impact", "Innovation"],
                "question_count": len(company_questions.get("Meta", []))
            }
        ]
    }
