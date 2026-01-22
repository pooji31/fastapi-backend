from fastapi import APIRouter, HTTPException
import os
import requests

router = APIRouter(prefix="/admin", tags=["AI Dashboard"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

students = [
    {"mail": "aryan@gmail.com", "name": "Aryan"},
    {"mail": "sneha@gmail.com", "name": "Sneha"},
    {"mail": "rahul@gmail.com", "name": "Rahul"},
]

code_ratings = [
    {"mail": "aryan@gmail.com", "topic": "Python Basics", "marks": 85},
    {"mail": "sneha@gmail.com", "topic": "Python Basics", "marks": 45},
    {"mail": "rahul@gmail.com", "topic": "Python Basics", "marks": 30},
]

@router.get("/top-students")
def top_students(n: int = 3):
    result = []
    for r in code_ratings:
        for s in students:
            if s["mail"] == r["mail"]:
                result.append({**s, "marks": r["marks"]})
    return sorted(result, key=lambda x: x["marks"], reverse=True)[:n]

@router.get("/weak-students")
def weak_students(threshold: int = 40):
    return [
        {**s, "marks": r["marks"]}
        for r in code_ratings
        for s in students
        if s["mail"] == r["mail"] and r["marks"] < threshold
    ]

@router.get("/skill-distribution")
def skill_distribution():
    return {
        "python": sum(1 for r in code_ratings if r["marks"] >= 50)
    }

@router.get("/ai-summary")
def ai_summary():
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set")

    prompt = f"""
    Top Students: {top_students()}
    Weak Students: {weak_students()}
    Skill Distribution: {skill_distribution()}
    Give a short placement summary.
    """

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=15,
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Groq API failed")

    return {"summary": response.json()["choices"][0]["message"]["content"]}
