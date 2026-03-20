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


def generate_debate_stance(topic: str, context: str = "") -> str:
    """Generate a plausible but incorrect stance on a topic to challenge the user."""
    prompt = f"""
You are acting as an AI Debater who is intentionally taking a flawed, provocative, or slightly incorrect stance on the topic: "{topic}".
Your goal is to challenge the user. Make an argument that sounds confident and plausible, but contains a fundamental misunderstanding or error based on the concepts in the provided context.

Context from course material:
{context[:3000]}

Rules:
1. Speak directly to the user in a challenging but friendly tone (e.g., "I actually don't think [topic] is that important because...").
2. Your argument MUST be noticeably flawed or incomplete according to the context provided.
3. Keep it to 2-3 short paragraphs max.
"""
    return generate_response(prompt)


def evaluate_debate_rebuttal(topic: str, user_rebuttal: str, context: str = "") -> str:
    """Evaluate if the user successfully countered the AI's flawed argument."""
    prompt = f"""
You previously took a flawed stance on the topic: "{topic}".
The user has provided a rebuttal to correct you.

User's Rebuttal:
"{user_rebuttal}"

Context from course material:
{context[:3000]}

If the user's rebuttal correctly identifies your flaw and uses facts from the context, concede defeat gracefully, praise their understanding, and declare them the winner!
If their rebuttal is weak, incorrect, or misses the point, push back slightly, explain what they missed, and let them know they haven't won the debate yet.

Output your response as if you are the AI Debater reacting to them. Format using markdown.
"""
    return generate_response(prompt)
