# 🧠 AI-Based Quiz App with Streamlit

**Ai_based_quizapp** is a smart and interactive quiz generator built using **Streamlit** and powered by **Gemini AI**. Just upload a document, and the app will automatically generate a multiple-choice quiz based on the content using AI — no manual question-writing needed!

---

## ✨ Features

- 📂 Upload any supported document (TXT) currently only text file supported
- 🤖 Automatically generate quiz questions using **Gemini API**
- 📝 Take multiple-choice quizzes in the browser
- ✅ Instant scoring and feedback
- 🧑‍🎓 Rank users based on their quiz performance (correct answers)
- 🎯 Clean, responsive UI built with Streamlit

---

## 🧠 How It Works

1. **Upload**: You provide a document with study content or reference material.
2. **Process**: Text is extracted and summarized.
3. **AI Generation**: The Gemini API generates quiz questions from the content.
4. **Interactive Quiz**: You answer MCQs directly in the app and get feedback.
5. **User Ranking**: The app ranks users based on the number of correct answers.(stores the data in the json file)

---

## 🚀 Tech Stack

- **Frontend/UI**: Streamlit
- **AI Engine**: Gemini API (Google's Generative AI)
- **Python Libraries**:  
  `streamlit`, `google-generativeai`, `pydantic`, `python-docx`

---

## 📦 Installation
.

```bash
git clone https://github.com/Abdevilji/Ai_based_quizapp.git
cd Ai_based_quizapp
pip install -r requirements.txt
streamlit run ai_quiz.py
```
Configure Gemini API Key
Create a .env file in the root directory of the project and add your Gemini API key:

.env file
GOOGLE_API_KEY_NEW=your_actual_api_key_here

⚠️ Important: Replace your_actual_api_key_here with your valid Gemini API key.
Do not share your API key publicly or push it to version control
