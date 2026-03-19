# StudyMate

**StudyMate** is an AI-powered study companion designed to help you interact with your PDF materials smarter and faster. Upload your notes or textbooks to get intelligent quizzes, interactive visuals, and deep learning feedback.

## ✨ Features

- 📑 **Smart PDF Uploads:** Automatically extracts text and intelligently classifies 5–8 key distinct study topics from your documents.
- 🎯 **AI-Generated Quizzes:** Generates MCQ quizzes matching your selected difficulty (Easy, Medium, Hard).
- 🎓 **Feynman Technique Simulator:** Test your true understanding. Explain a concept in your own words, and let the AI grade your explanation against your study materials to find gaps in your knowledge. 
- 🧠 **Concept Mind Maps:** Highly interactive visual diagrams mapping out the key concepts in your document using beautiful `mermaid.js` flowcharts.
- 🔊 **Text-to-Speech (TTS):** Native browser voice integration that reads aloud explanations, answers, and quiz questions. 
- 🤖 **AI Tutor Chats:** Ask the built-in AI tutor specific questions about your uploaded materials at any time.
- 📊 **Dynamic Dashboard:** Track your topics studied, avg scores, quizzes taken, and view a personalized revision plan generated directly from your weak areas.

## 🚀 Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your Groq API key:
   Put your `GROQ_API_KEY` in `app/config.py`.
3. Run the FastAPI backend:
   ```bash
   python -m uvicorn app.server:app --reload
   ```
4. Open `index.html` in your web browser. Enjoy studying smarter!