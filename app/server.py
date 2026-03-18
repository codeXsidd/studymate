from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import shutil, os, json, re

from app.ai_engine import generate_response, classify_topics, generate_quiz
from app.pdf_processor import extract_text_from_pdf

app = FastAPI(title="StudyMate API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

stored_topics: list[str] = []
stored_text: str = ""


# ───────── HELPERS ─────────

def extract_json_array(raw: str) -> list:
    """Robustly extract a JSON array from a raw LLM response."""
    if not raw:
        return []

    # 1. Try direct parse
    try:
        parsed = json.loads(raw.strip())
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown code fences  ```json ... ```
    cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # 3. Extract first [...] block
    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    return []


# ───────── ROUTES ─────────

@app.get("/", response_class=HTMLResponse)
async def home():
    index_path = "index.html"
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse("<h2>StudyMate API is running. Serve index.html from your frontend.</h2>")


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = extract_text_from_pdf(path)
    if not text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from PDF.")

    global stored_text, stored_topics
    stored_text = text

    topics_raw = classify_topics(text)

    # Clean up: remove numbering like "1. ", "- ", empty lines
    topics = []
    for line in topics_raw.split("\n"):
        line = re.sub(r"^\s*[\d\-\*\.]+\s*", "", line).strip()
        if line and len(line) > 2:
            topics.append(line)

    stored_topics = topics[:8]  # cap at 8

    return {"detected_topics": stored_topics}


class QuizRequest(BaseModel):
    topic: str
    difficulty: str = "easy"


@app.post("/quiz/")
async def quiz(data: QuizRequest):
    raw = generate_quiz(data.topic, data.difficulty)
    questions = extract_json_array(raw)

    # Validate structure
    valid = []
    for q in questions:
        if isinstance(q, dict) and "question" in q and "options" in q and "answer" in q:
            if isinstance(q["options"], list) and len(q["options"]) >= 2:
                valid.append(q)

    if not valid:
        raise HTTPException(status_code=500, detail="AI returned invalid quiz format. Please retry.")

    return {"quiz": valid}


class TutorRequest(BaseModel):
    question: str


@app.post("/ai-tutor/")
async def ai_tutor(data: TutorRequest):
    if not data.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    context = f"\n\nContext from uploaded PDF:\n{stored_text[:2000]}" if stored_text else ""
    prompt = (
        f"You are a friendly, knowledgeable study tutor. "
        f"Explain the following clearly with examples and structure your answer with markdown headers and bullet points where appropriate.{context}\n\n"
        f"Question: {data.question}"
    )
    answer = generate_response(prompt)
    return {"answer": answer}


class TopicRequest(BaseModel):
    topic: str


@app.post("/explain-topic/")
async def explain_topic(data: TopicRequest):
    context = f"\n\nRelevant context:\n{stored_text[:2000]}" if stored_text else ""
    prompt = (
        f"You are a study tutor. Give a clear, beginner-friendly explanation of **{data.topic}**. "
        f"Use markdown with: a short intro, key concepts as bullet points, a simple example, and a one-sentence summary.{context}"
    )
    explanation = generate_response(prompt)
    return {"explanation": explanation}
