from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import shutil, os, json, re, uuid

from app.ai_engine import (
    generate_response,
    classify_topics,
    generate_quiz,
    evaluate_explanation,
    generate_mindmap,
    generate_debate_stance,
    evaluate_debate_rebuttal,
    generate_scenario,
    evaluate_scenario_action
)
from app.pdf_processor import extract_text_from_pdf

app = FastAPI(title="StudyMate API", version="2.1")

app.mount("/static", StaticFiles(directory=".", html=True), name="static")

@app.get("/sitemap.xml")
async def sitemap():
    return FileResponse("sitemap.xml", media_type="application/xml")

@app.get("/robots.txt")
async def robots():
    return FileResponse("robots.txt", media_type="text/plain")

@app.get("/about")
def about():
    return FileResponse("about.html")

@app.get("/features")
def features():
    return FileResponse("features.html")

@app.get("/how-it-works")
def how_it_works():
    return FileResponse("how-it-works.html")

@app.get("/login")
def login_page():
    return FileResponse("login.html")

@app.get("/register")
def register_page():
    return FileResponse("register.html")

# ✅ CORS (IMPORTANT FOR MOBILE + RENDER)
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


# ───────── HEALTH CHECK ─────────
@app.get("/health")
def health():
    return {"status": "ok"}


# ───────── HELPERS ─────────
def extract_json_array(raw: str) -> list:
    if not raw:
        return []

    try:
        parsed = json.loads(raw.strip())
        if isinstance(parsed, list):
            return parsed
    except:
        pass

    cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return parsed
    except:
        pass

    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, list):
                return parsed
        except:
            pass

    return []


# ───────── ROUTES ─────────

@app.get("/", response_class=HTMLResponse)
async def home():
    index_path = "index.html"
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse("<h2>StudyMate API is running.</h2>")


def get_stored_text() -> str:
    global stored_text
    if stored_text:
        return stored_text
    # Fallback to recover from the latest uploaded file in the uploads directory
    try:
        files = os.listdir(UPLOAD_FOLDER)
        pdfs = [f for f in files if f.endswith('.pdf')]
        if pdfs:
            pdfs.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)
            text = extract_text_from_pdf(os.path.join(UPLOAD_FOLDER, pdfs[0]))
            if text:
                stored_text = text
                return stored_text
    except Exception:
        pass
    return ""


# 🔥 FIXED UPLOAD (IMPORTANT)
@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        # ✅ Unique filename (prevents overwrite issues)
        unique_name = f"{uuid.uuid4()}_{file.filename}"
        path = os.path.join(UPLOAD_FOLDER, unique_name)

        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        text = extract_text_from_pdf(path)

        if not text or not text.strip():
            raise HTTPException(status_code=422, detail="Could not extract text from PDF.")

        global stored_text, stored_topics
        stored_text = text

        topics_raw = classify_topics(text)

        topics = []
        for line in topics_raw.split("\n"):
            line = re.sub(r"^\s*[\d\-\*\.]+\s*", "", line).strip()
            if line and len(line) > 2:
                topics.append(line)

        stored_topics = topics[:8]

        return {"detected_topics": stored_topics}

    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Upload failed on server.")


# ───────── QUIZ ─────────
class QuizRequest(BaseModel):
    topic: str
    difficulty: str = "easy"


@app.post("/quiz/")
async def quiz(data: QuizRequest):
    try:
        raw = generate_quiz(data.topic, data.difficulty)
        questions = extract_json_array(raw)

        valid = []
        for q in questions:
            if isinstance(q, dict) and "question" in q and "options" in q and "answer" in q:
                if isinstance(q["options"], list) and len(q["options"]) >= 2:
                    valid.append(q)

        if not valid:
            raise HTTPException(status_code=500, detail="Invalid quiz format.")

        return {"quiz": valid}

    except Exception as e:
        print("QUIZ ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Quiz generation failed.")


# ───────── AI TUTOR ─────────
class TutorRequest(BaseModel):
    question: str


@app.post("/ai-tutor/")
async def ai_tutor(data: TutorRequest):
    try:
        if not data.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty.")

        context_text = get_stored_text()
        context = f"\n\nContext:\n{context_text[:2000]}" if context_text else ""

        prompt = (
            f"You are a friendly tutor. Explain clearly with examples.\n\n"
            f"{context}\n\nQuestion: {data.question}"
        )

        answer = generate_response(prompt)

        return {"answer": answer}

    except Exception as e:
        print("TUTOR ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Tutor failed.")


# ───────── EXPLAIN TOPIC ─────────
class TopicRequest(BaseModel):
    topic: str


@app.post("/explain-topic/")
async def explain_topic(data: TopicRequest):
    try:
        context_text = get_stored_text()
        context = f"\n\nContext:\n{context_text[:2000]}" if context_text else ""

        prompt = (
            f"Explain {data.topic} simply with bullets, example, and summary.\n"
            f"{context}"
        )

        explanation = generate_response(prompt)

        return {"explanation": explanation}

    except Exception as e:
        print("EXPLAIN ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Explanation failed.")

# ───────── FEYNMAN TECHNIQUE ─────────
class FeynmanRequest(BaseModel):
    topic: str
    explanation: str

@app.post("/feynman-evaluate/")
async def feynman_evaluate(data: FeynmanRequest):
    try:
        if not data.topic.strip() or not data.explanation.strip():
            raise HTTPException(status_code=400, detail="Topic and explanation cannot be empty.")

        context_text = get_stored_text()
        context = context_text if context_text else ""
        feedback = evaluate_explanation(data.topic, data.explanation, context)

        return {"feedback": feedback}

    except Exception as e:
        print("FEYNMAN ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Feynman evaluation failed.")

# ───────── MIND MAP ─────────
@app.post("/generate-mindmap/")
async def generate_mindmap_endpoint():
    try:
        context_text = get_stored_text()
        if not context_text:
            raise HTTPException(status_code=400, detail="No document uploaded yet.")

        mindmap_raw = generate_mindmap(context_text)
        mindmap_cleaned = mindmap_raw.replace("```mermaid", "").replace("```", "").strip()

        return {"mindmap": mindmap_cleaned}

    except HTTPException:
        raise
    except Exception as e:
        print("MINDMAP ERROR:", str(e))
        raise HTTPException(status_code=500, detail=f"Mind map generation failed: {str(e)} -- Type: {type(e).__name__}")


# ───────── DEBATE AI ─────────
class DebateStartRequest(BaseModel):
    topic: str

@app.post("/debate-start/")
async def debate_start(data: DebateStartRequest):
    try:
        if not data.topic.strip():
            raise HTTPException(status_code=400, detail="Topic cannot be empty.")

        context_text = get_stored_text()
        context = context_text if context_text else ""
        stance = generate_debate_stance(data.topic, context)

        return {"stance": stance}

    except Exception as e:
        print("DEBATE START ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Debate start failed.")

class DebateRebuttalRequest(BaseModel):
    topic: str
    rebuttal: str

@app.post("/debate-rebuttal/")
async def debate_rebuttal(data: DebateRebuttalRequest):
    try:
        if not data.topic.strip() or not data.rebuttal.strip():
            raise HTTPException(status_code=400, detail="Topic and rebuttal cannot be empty.")

        context_text = get_stored_text()
        context = context_text if context_text else ""
        feedback = evaluate_debate_rebuttal(data.topic, data.rebuttal, context)

        return {"feedback": feedback}

    except Exception as e:
        print("DEBATE REBUTTAL ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Debate rebuttal failed.")

# ───────── SCENARIO SIMULATOR ─────────
class ScenarioStartRequest(BaseModel):
    topic: str

@app.post("/scenario-start/")
async def scenario_start(data: ScenarioStartRequest):
    try:
        if not data.topic.strip():
            raise HTTPException(status_code=400, detail="Topic cannot be empty.")

        context_text = get_stored_text()
        context = context_text if context_text else ""
        scenario = generate_scenario(data.topic, context)

        return {"scenario": scenario}

    except Exception as e:
        print("SCENARIO START ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Scenario start failed.")

class ScenarioActionRequest(BaseModel):
    topic: str
    action: str

@app.post("/scenario-action/")
async def scenario_action(data: ScenarioActionRequest):
    try:
        if not data.topic.strip() or not data.action.strip():
            raise HTTPException(status_code=400, detail="Topic and action cannot be empty.")

        context_text = get_stored_text()
        context = context_text if context_text else ""
        feedback = evaluate_scenario_action(data.topic, data.action, context)

        return {"feedback": feedback}

    except Exception as e:
        print("SCENARIO ACTION ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Scenario action failed.")