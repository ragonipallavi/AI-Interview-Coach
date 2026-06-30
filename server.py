"""
AI Interview Coach — FastAPI Backend
Run: python server.py
Opens: http://localhost:8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import json, os, re, asyncio
from datetime import datetime
import ollama

app = FastAPI(title="AI Interview Coach")

# ── Serve static frontend ─────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")


# ═══════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════
class StartRequest(BaseModel):
    role: str
    level: str
    interview_type: str   # "HR" | "Technical" | "Mixed"
    num_questions: int
    model: str = "llama3"

class AnswerRequest(BaseModel):
    question: str
    answer: str
    role: str
    level: str
    model: str = "llama3"

class ResumeRequest(BaseModel):
    resume_text: str
    num_questions: int = 5
    model: str = "llama3"


# ═══════════════════════════════════════════════════════════════
# QUESTION GENERATION
# ═══════════════════════════════════════════════════════════════
HR_FALLBACK = [
    "Tell me about yourself and your professional journey.",
    "What are your greatest strengths and how have they helped you?",
    "Describe a challenging situation at work and how you handled it.",
    "Where do you see yourself in 5 years?",
    "Why should we hire you over other candidates?",
    "How do you handle pressure or tight deadlines?",
    "Tell me about your biggest professional achievement.",
    "Describe a time you had to learn a new skill quickly.",
    "How do you prioritize when you have competing deadlines?",
    "What motivates you to do your best work?",
]

TECH_FALLBACK = {
    "default": [
        "Explain the difference between a stack and a queue.",
        "What is time complexity? Explain Big O notation.",
        "Describe the SOLID principles in object-oriented programming.",
        "What is the difference between REST and GraphQL?",
        "How does garbage collection work in modern languages?",
    ],
    "Data Scientist": [
        "Explain the bias-variance tradeoff with an example.",
        "How would you handle class imbalance in a classification problem?",
        "What is the difference between supervised and unsupervised learning?",
        "Explain how gradient boosting works.",
        "Write a SQL query to find the top 3 products by sales per region.",
    ],
    "ML Engineer": [
        "What is the difference between batch normalization and layer normalization?",
        "Explain how attention mechanisms work in transformers.",
        "How do you prevent overfitting in deep neural networks?",
        "What is the difference between fine-tuning and training from scratch?",
        "Explain embeddings and how they are used in NLP.",
    ],
    "Frontend Developer": [
        "Explain the virtual DOM in React and why it improves performance.",
        "What is the difference between CSS Grid and Flexbox?",
        "How does JavaScript event bubbling work?",
        "Explain closures in JavaScript with an example.",
        "What are React hooks? Explain useState and useEffect.",
    ],
    "Data Analyst": [
        "What is the difference between INNER JOIN and LEFT JOIN in SQL?",
        "How would you detect outliers in a dataset?",
        "Explain the difference between mean, median, and mode.",
        "What is a pivot table and when would you use one?",
        "How do you handle missing data in analysis?",
    ],
}

def _call_ollama(prompt: str, model: str) -> str:
    try:
        resp = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.7, "num_predict": 150}
        )
        return resp["message"]["content"].strip()
    except Exception:
        return ""

def _clean_question(raw: str) -> str:
    for prefix in ["Question:", "Q:", "Interview Question:", "HR Question:", "Technical Question:"]:
        if raw.startswith(prefix):
            raw = raw[len(prefix):].strip()
    # Remove leading numbers like "1. " or "1) "
    raw = re.sub(r"^[\d]+[.):\s]+", "", raw).strip()
    return raw

def generate_question(role: str, level: str, itype: str, model: str, idx: int) -> str:
    if itype == "HR":
        prompt = f"""You are an experienced HR interviewer.
Generate exactly ONE behavioral/HR interview question for a {level}-level {role}.
Question #{idx}. Make it open-ended. Return ONLY the question, no numbering, no preamble."""
    else:
        difficulty = {"Fresher":"basic","Junior":"intermediate","Mid":"intermediate to advanced",
                      "Senior":"advanced","Lead":"expert/architectural"}.get(level,"intermediate")
        prompt = f"""You are a senior technical interviewer at a top tech company.
Generate exactly ONE technical interview question for a {level}-level {role}.
Difficulty: {difficulty}. Question #{idx}.
Return ONLY the question itself, no numbering, no preamble, no answer."""

    raw = _call_ollama(prompt, model)
    q   = _clean_question(raw)

    if not q or len(q) < 10:
        if itype == "HR":
            return HR_FALLBACK[(idx-1) % len(HR_FALLBACK)]
        else:
            bank = TECH_FALLBACK.get(role, TECH_FALLBACK["default"])
            return bank[(idx-1) % len(bank)]
    return q


@app.post("/api/start")
def start_interview(req: StartRequest):
    questions = []
    for i in range(req.num_questions):
        if req.interview_type == "HR":
            itype = "HR"
        elif req.interview_type == "Technical":
            itype = "Technical"
        else:
            itype = "HR" if i % 2 == 0 else "Technical"
        q = generate_question(req.role, req.level, itype, req.model, i+1)
        questions.append({"text": q, "type": itype})
    return {"questions": questions}


# ═══════════════════════════════════════════════════════════════
# ANSWER SCORING
# ═══════════════════════════════════════════════════════════════
FILLER_WORDS = ["um","uh","like","basically","literally","you know",
                "sort of","kind of","actually","honestly"]

def _confidence_score(answer: str) -> float:
    words = answer.lower().split()
    if not words:
        return 0.0
    hedges    = sum(answer.lower().count(h) for h in ["maybe","perhaps","i think","i guess","not sure","probably"])
    fillers   = sum(answer.lower().count(f) for f in FILLER_WORDS)
    confident = sum(answer.lower().count(c) for c in ["definitely","specifically","for example",
                    "i built","i designed","i led","i implemented","i achieved","in my experience"])
    length_f  = min(1.0, len(words) / 50)
    score     = 7.0 - hedges*0.4 - fillers*0.3 + confident*0.5
    return round(max(0.0, min(10.0, score * length_f)), 1)

def _heuristic_score(answer: str) -> dict:
    wc      = len(answer.split())
    ls      = min(10, wc / 20)
    ss      = min(10, len([s for s in answer.split('.') if s.strip()]) * 1.5)
    overall = round(max(1, min(10, (ls + ss) / 2)), 1)
    return {"technical": round(overall*0.9,1), "clarity": round(ss,1),
            "relevance": round(overall,1), "depth": round(ls,1),
            "overall": overall, "confidence": _confidence_score(answer),
            "feedback": "Structure your answer with a clear intro, example, and conclusion. Be specific."}

@app.post("/api/score")
def score_answer(req: AnswerRequest):
    if not req.answer.strip() or req.answer == "[Skipped]":
        return {"technical":0,"clarity":0,"relevance":0,"depth":0,"overall":0,"confidence":0,"feedback":"No answer provided."}

    prompt = f"""You are an expert interview evaluator.

Role: {req.role} | Level: {req.level}
Question: {req.question}
Answer: {req.answer}

Score on 0-10 for: technical_accuracy, clarity, relevance, depth.
overall = weighted average (tech 40%, clarity 30%, relevance 20%, depth 10%).
feedback = 2-3 sentences of specific actionable improvement tips.

Respond ONLY with valid JSON, no markdown:
{{"technical_accuracy":0,"clarity":0,"relevance":0,"depth":0,"overall":0,"feedback":""}}"""

    try:
        resp = ollama.chat(
            model=req.model,
            messages=[{"role":"user","content":prompt}],
            options={"temperature":0.2,"num_predict":300}
        )
        raw = resp["message"]["content"].strip()
        m   = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            d = json.loads(m.group())
            return {
                "technical":   float(d.get("technical_accuracy", d.get("technical", 5))),
                "clarity":     float(d.get("clarity", 5)),
                "relevance":   float(d.get("relevance", 5)),
                "depth":       float(d.get("depth", 5)),
                "overall":     float(d.get("overall", 5)),
                "confidence":  _confidence_score(req.answer),
                "feedback":    str(d.get("feedback","Keep practicing.")),
            }
    except Exception:
        pass
    result = _heuristic_score(req.answer)
    result["confidence"] = _confidence_score(req.answer)
    return result


# ═══════════════════════════════════════════════════════════════
# RESUME-BASED QUESTIONS
# ═══════════════════════════════════════════════════════════════
@app.post("/api/resume-questions")
def resume_questions(req: ResumeRequest):
    text = req.resume_text[:3000]
    prompt = f"""Analyze this resume and generate {req.num_questions} specific interview questions
based on the candidate's actual experience, projects, and skills.

RESUME:
{text}

Return ONLY the questions numbered 1 to {req.num_questions}, one per line."""

    try:
        resp = ollama.chat(
            model=req.model,
            messages=[{"role":"user","content":prompt}],
            options={"temperature":0.6,"num_predict":500}
        )
        raw  = resp["message"]["content"].strip()
        lines = [re.sub(r"^[\d]+[.):\s]+","",l).strip() for l in raw.split("\n") if l.strip()]
        qs    = [l for l in lines if len(l)>10][:req.num_questions]
        if qs:
            return {"questions": [{"text":q,"type":"Resume"} for q in qs]}
    except Exception:
        pass
    return {"questions": [{"text":f"Tell me about a project from your resume (#{i+1})","type":"Resume"} for i in range(req.num_questions)]}


# ═══════════════════════════════════════════════════════════════
# SAVE REPORT
# ═══════════════════════════════════════════════════════════════
class ReportRequest(BaseModel):
    data: dict

@app.post("/api/save-report")
def save_report(req: ReportRequest):
    os.makedirs("feedback", exist_ok=True)
    fname = f"feedback/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w") as f:
        json.dump(req.data, f, indent=2)
    return {"saved": fname}


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    import webbrowser

    url = "http://localhost:8000"

    print("\n🎯 AI Interview Coach")
    print(f"→ {url}\n")

    # Opens browser automatically
    webbrowser.open(url)

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
