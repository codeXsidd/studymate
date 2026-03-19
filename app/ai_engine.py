from groq import Groq
from app.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def generate_response(prompt: str, model: str = "llama-3.3-70b-versatile") -> str:
    """Send a prompt to Groq and return the response text."""
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=0.7,
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Error calling AI: {str(e)}"


def classify_topics(text: str) -> str:
    """Extract 5–8 key study topics from document text."""
    prompt = (
        "You are a curriculum assistant. From the following text, extract exactly 6 distinct, "
        "concise study topics (2–6 words each). Output only the topic names, one per line, "
        "with no numbering, bullets, or extra commentary.\n\n"
        f"Text:\n{text[:3000]}"
    )
    return generate_response(prompt)


def generate_quiz(topic: str, difficulty: str = "easy") -> str:
    """Generate 5 MCQ questions for a topic at the given difficulty level."""

    difficulty_guide = {
        "easy": "basic recall and definitions, suitable for beginners",
        "medium": "conceptual understanding and application",
        "hard": "analysis, edge cases, and advanced application",
    }.get(difficulty, "basic recall")

    prompt = f"""
You are an expert quiz generator. Create exactly 5 multiple-choice questions on the topic: "{topic}".
Difficulty level: {difficulty} — focus on {difficulty_guide}.

Requirements:
- Each question must have exactly 4 options labeled as full answer strings (not "A", "B", etc.)
- The "answer" field must be the EXACT TEXT of the correct option (matching one of the options strings exactly)
- Questions should be clear, unambiguous, and educational
- Vary the question types (definition, example, application)

Return ONLY a valid JSON array — no explanation, no markdown, no extra text:
[
  {{
    "question": "Question text here?",
    "options": ["Option one", "Option two", "Option three", "Option four"],
    "answer": "Option one"
  }}
]
"""
    return generate_response(prompt)


def evaluate_explanation(topic: str, explanation: str, context: str = "") -> str:
    """Evaluate a user's explanation of a topic using the Feynman technique."""
    prompt = f"""
You are an expert tutor evaluating a student's explanation using the Feynman Technique.
The student is trying to explain the topic: "{topic}".

Student's Explanation:
"{explanation}"

Context from course material:
{context[:3000]}

Evaluate the explanation based on the following:
1. Is it factually correct according to the context?
2. Is it simple and easy to understand (like explaining to a 5-year-old)?
3. What critical information from the context is missing?

Provide constructive feedback. Highlight what they got right, point out any misconceptions, and gently ask a follow-up question to test the missing knowledge. Keep it encouraging and concise.
"""
    return generate_response(prompt)


def generate_mindmap(text: str) -> str:
    """Generate a Mermaid.js graph based on the document text."""
    prompt = f"""
Analyze the following text and extract the key concepts and their relationships.
Create a Mermaid.js flowchart (graph TD) that visually represents these concepts as a mind map.

Rules:
- Output ONLY valid Mermaid code starting with `graph TD`.
- Do not use markdown code blocks (e.g. ```mermaid).
- Do not include any HTML, explanations, or extra text.
- Use simple, short node names.
- Connect related concepts logically.
- Keep the graph concise but comprehensive (max 15-20 nodes).

Text:
{text[:4000]}
"""
    return generate_response(prompt)
