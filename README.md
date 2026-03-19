# StudyMate 📚🤖

StudyMate is an AI-powered study companion designed to make learning smarter, faster, and more interactive. Simply upload any PDF, and the application uses advanced language models to generate tailored quizzes, personalized explanations, and track your weak areas over time.

## 🚀 Features

StudyMate goes beyond traditional learning by incorporating highly interactive, scientifically proven learning methods:

### 🎓 **Feynman Technique Simulator (Teach the AI)**
Instead of the AI lecturing you, **you teach the AI**. 
- Enter a topic and explain it in your own words.
- The AI adopts the persona of a beginner student and evaluates your explanation against the context of your uploaded course material.
- It highlights what you got right, points out any misconceptions, and asks targeted questions to test gaps in your knowledge. 

### 🧠 **Interactive Concept Mind Maps**
For visual learners, reading endless text can be tiring.
- With one click, StudyMate extracts the core concepts from your document and automatically generates a beautiful, interactive **visual flowchart** natively in your browser using Mermaid.js.
- Perfect for understanding how different concepts connect.

### 🔊 **Text-to-Speech Accessibility**
- Read along with auditory learning! Sleek **🔊 Read** buttons are integrated throughout the application.
- Listen to topic explanations, AI tutor answers, and quiz questions out loud to improve retention.

### 📝 **AI Quiz Generation & Dashboard**
- Intelligent extraction of 5-8 distinct study topics from your document.
- Multiple-choice quizzes dynamically generated at varying difficulties (Easy, Medium, Hard).
- A detailed **Dashboard** tracking your average scores, areas of weakness, and generating a personalized revision plan.

## ⚙️ How to Run Locally

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Make sure you have your Groq API key set up (or update `app/config.py`).
3. Start the FastAPI server:
   ```bash
   python -m uvicorn app.server:app --reload
   ```
4. Open the interface in your browser:
   ```text
   http://127.0.0.1:8000
   ```

## 🛠️ Built With
- **Frontend**: Vanilla JavaScript, HTML5, CSS3, Mermaid.js
- **Backend**: Python, FastAPI
- **AI Processing**: Groq LLM API (`llama-3.3-70b-versatile`)