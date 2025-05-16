import streamlit as st
import os
import json
from google import genai
from google.genai.types import GenerateContentConfig
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

SCORE_FILE = "scores.json"

class Packet(BaseModel):
    question: str
    choices: list[str]
    correct_answer: str
    explanation: str

class QuizPacket(BaseModel):
    questions: list[Packet]

def load_scores():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_scores(scores):
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f, indent=4)

def reset_all():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()  # Resets the app and state

def get_questions( context_text):
    prompt = f"""Using the following text as context, randomly select and extract content from different sections to generate 10 diverse quiz questions. Ensure that the selection of topics varies with each run to simulate random sampling from the text:

{context_text}

For each question:
- Provide four multiple choice options (A, B, C, D), only one of which is correct.
- Vary the position of the correct answer.

Ensure that questions are based on different sections of the context and do not follow a fixed or sequential order.

Return the result as a JSON array of 10 objects, each with these keys: 'question', 'choices', 'correct_answer'.
"""

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=QuizPacket,
        ),
    )
    return json.loads(response.text)["questions"]

def show_leaderboard():
    st.sidebar.markdown("### 🏆 Leaderboard")
    sorted_scores = sorted(st.session_state.user_scores.items(), key=lambda x: x[1], reverse=True)
    for i, (user, score) in enumerate(sorted_scores, 1):
        st.sidebar.write(f"{i}. {user}: {score}")

def load_context_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def initial_form():
    st.title("🧠 Lets see How much You know about")
    st.markdown("Please enter your details to begin:")

    # Directly load file content from local storage
    file_content = load_context_from_file("details.txt")

    with st.form("user_init_form"):
        username = st.text_input("Username")
        # age = st.slider("Select your AGE:", 10, 40, 15)
        subject = "company"
        submitted = st.form_submit_button("Start Quiz")

    if submitted:
        if username in st.session_state.user_scores:
            st.warning("Username already exists! Please choose another.")
        elif not username:
            st.warning("Please enter a username.")
        else:
            st.session_state.username = username
            # st.session_state.age = age
            st.session_state.subject = subject
            st.session_state.context_text = file_content
            st.session_state.user_scores[username] = 0
            save_scores(st.session_state.user_scores)
            with st.spinner("Generating quiz questions..."):
                st.session_state.quiz_data = get_questions( file_content)
            st.session_state.current_question_index = 0
            st.session_state.form_count = 0
            st.rerun()


def quiz_flow():
    st.title("🧠 Quiz from the provided details.txt file")
    st.sidebar.write(f"User: {st.session_state.username}")
    show_leaderboard()
    # st.markdown(f"**Subject:** {st.session_state.subject} | **Age:** {st.session_state.age}")
    
    current_index = st.session_state.current_question_index
    total_questions = len(st.session_state.quiz_data)
    
    st.progress((current_index) / total_questions)
    st.write(f"Question {current_index + 1} of {total_questions}")
    
    current_quiz = st.session_state.quiz_data[current_index]
    
    question_key = f"submitted_{current_index}"

    with st.form(key=f"quiz_form_{current_index}"):
        st.markdown(f"### Q: {current_quiz['question']}")
        user_choice = st.radio(
        "Choose your answer:",
        current_quiz['choices'],
        key=f"choice_{current_index}",
        disabled=st.session_state.get(question_key, False)
        )

        submitted = st.form_submit_button("Submit", disabled=st.session_state.get(question_key, False))

        if submitted:
            if user_choice == current_quiz['correct_answer']:
                st.session_state.user_scores[st.session_state.username] += 1
                save_scores(st.session_state.user_scores)
            st.session_state[question_key] = True  # ✅ Lock this question
            st.session_state.question_answered = True
            st.rerun()

    # with st.form(key=f"quiz_form_{current_index}"):
    #     st.markdown(f"### Q: {current_quiz['question']}")
    #     user_choice = st.radio("Choose your answer:", current_quiz['choices'], key=f"choice_{current_index}")
        
    #     # Disable submit button if already submitted for this question
    #     submitted = st.form_submit_button("Submit", disabled=st.session_state.get(question_key, False))
        
    #     if submitted:
    #         if user_choice == current_quiz['correct_answer']:
    #             st.session_state.user_scores[st.session_state.username] += 1
    #             save_scores(st.session_state.user_scores)
    #             # st.success("✅ Correct!")
    #         # else:
    #             # st.error("❌ Incorrect!")
    #         # st.info(f"💡 Explanation: {current_quiz['explanation']}")
    #         st.session_state[question_key] = False  # Lock this question
    #         st.session_state.question_answered = True
    #         st.rerun()

    # Handle question navigation outside the form
    if st.session_state.get('question_answered', False):
        st.markdown("---")
        if current_index < total_questions - 1:
            if st.button("Next Question"):
                st.session_state.current_question_index += 1
                st.session_state.question_answered = False
                st.rerun()
        else:
            st.balloons()
            st.success(f"Quiz complete! Your score: {st.session_state.user_scores[st.session_state.username]}/{total_questions}")
            if st.button("Start New Quiz"):
                reset_all()

def main():
    # Top-right Restart button
    st.markdown(
        "<div style='position: fixed; top: 10px; right: 10px;'>"
        "<form action='#' method='post'>"
        "<button type='submit' name='restart' style='background-color:#f44336; color:white; border:none; padding:8px 16px; border-radius:4px;'>Restart</button>"
        "</form>"
        "</div>",
        unsafe_allow_html=True,
    )
    if st.session_state.get('restart', False) or st.button("Restart", key="restart_btn", help="Restart the quiz", type="primary"):
        reset_all()

    if "user_scores" not in st.session_state:
        st.session_state.user_scores = load_scores()

    if "username" not in st.session_state:
        initial_form()
    else:
        quiz_flow()

if __name__ == '__main__':
    api_key = os.environ.get('GOOGLE_API_KEY_NEW')
    client = genai.Client(api_key=api_key)
    MODEL_ID = "gemini-2.0-flash-001"
    main()

