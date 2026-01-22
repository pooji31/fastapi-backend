
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found")

# Groq client
client = Groq(api_key=GROQ_API_KEY)
GROQ_MODEL = "llama-3.1-8b-instant"

# FastAPI app
app = FastAPI(title="AI Coding Question Generator", version="1.0.0")

# Request model
class QuestionRequest(BaseModel):
    topic: str
    difficulty: str
    language: str  # c / cpp / python

# Build prompt
def build_prompt(topic: str, difficulty: str, language: str) -> str:
    return f"""
You are an API that generates coding questions.

Topic: {topic}
Difficulty: {difficulty}
Language: {language}

Respond ONLY with valid JSON.
NO markdown.
NO explanation.
NO extra text.

STRICT JSON FORMAT:
{{
  "question": "string",
  "constraints": "string",
  "input_format": "string",
  "output_format": "string",
  "sample_input": "string",
  "sample_output": "string",
  "test_cases": [
    {{
      "input": "string",
      "output": "string"
    }}
  ]
}}
"""

# API endpoint
@app.post("/generate-question")
def generate_question(req: QuestionRequest):
    try:
        prompt = build_prompt(req.topic, req.difficulty, req.language)

        # Call Groq API
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "Return strict JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        # Safe parsing
        try:
            content = response.choices[0].message.content
            data = json.loads(content)
        except Exception as parse_err:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse Groq response: {parse_err}\nRaw response: {response}"
            )

        # Validate keys
        required_keys = [
            "question", "constraints", "input_format", "output_format",
            "sample_input", "sample_output", "test_cases"
        ]
        for key in required_keys:
            if key not in data:
                raise HTTPException(status_code=500, detail=f"Missing key in response: {key}")

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")
