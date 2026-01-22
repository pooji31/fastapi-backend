from ai_summary import generate_ai_summary

from fastapi import FastAPI
from dummy_data import students, code_ratings

app = FastAPI(title="Heedsites AI Dashboard")

@app.get("/admin/top-students")
def get_top_students(n: int = 3):
    # combine student + marks
    result = []

    for rating in code_ratings:
        for student in students:
            if rating["mail"] == student["mail"]:
                result.append({
                    "name": student["firstname"],
                    "mail": student["mail"],
                    "marks": rating["marks"]
                })

    # sort by marks (high → low)
    result.sort(key=lambda x: x["marks"], reverse=True)

    return result[:n]
@app.get("/admin/weak-students")
def get_weak_students(threshold: int = 40):
    weak = []

    for rating in code_ratings:
        if rating["marks"] < threshold:
            for student in students:
                if student["mail"] == rating["mail"]:
                    weak.append({
                        "name": student["firstname"],
                        "mail": student["mail"],
                        "marks": rating["marks"]
                    })

    return weak
@app.get("/admin/skill-distribution")
def skill_distribution():
    skills = {
        "python": 0,
        "frontend": 0,
        "backend": 0
    }

    for rating in code_ratings:
        topic = rating["topic"].lower()
        marks = rating["marks"]

        if marks >= 50:
            if "python" in topic:
                skills["python"] += 1
            if "frontend" in topic:
                skills["frontend"] += 1
            if "backend" in topic:
                skills["backend"] += 1

    return skills
@app.get("/admin/ai-summary")
def ai_summary():
    top = get_top_students()
    weak = get_weak_students()
    skills = skill_distribution()

    summary = generate_ai_summary(top, weak, skills)

    return {"summary": summary}
