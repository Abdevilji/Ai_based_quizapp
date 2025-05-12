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

def get_questions(age, subject, context_text):
    prompt = f"""Using the following text as context, generate 10  quiz questions to help prepare for a Competition:

{context_text}

For each question, provide four multiple choice options (A, B, C, D) where only one is correct. Make sure the correct answer is not always the same letter. For each question, also provide an explanation for the correct answer.

Return the response as a JSON array containing 10 objects, each with the keys 'question', 'choices', 'correct_answer', and 'explanation'.
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
    st.title("🧠 STEM Quiz for Kids")
    st.markdown("Please enter your details to begin:")

    # Directly load file content from local storage
    file_content = load_context_from_file("details.txt")

    with st.form("user_init_form"):
        username = st.text_input("Username")
        age = st.slider("Select your AGE:", 10, 40, 15)
        subject = "company"
        submitted = st.form_submit_button("Start Quiz")

    if submitted:
        if username in st.session_state.user_scores:
            st.warning("Username already exists! Please choose another.")
        elif not username:
            st.warning("Please enter a username.")
        else:
            st.session_state.username = username
            st.session_state.age = age
            st.session_state.subject = subject
            st.session_state.context_text = file_content
            st.session_state.user_scores[username] = 0
            save_scores(st.session_state.user_scores)
            with st.spinner("Generating quiz questions..."):
                st.session_state.quiz_data = get_questions(age, subject, file_content)
            st.session_state.current_question_index = 0
            st.session_state.form_count = 0
            st.rerun()


def quiz_flow():
    st.title("🧠 Quiz from the provided details.txt file")
    st.sidebar.write(f"User: {st.session_state.username}")
    show_leaderboard()
    st.markdown(f"**Subject:** {st.session_state.subject} | **Age:** {st.session_state.age}")
    
    current_index = st.session_state.current_question_index
    total_questions = len(st.session_state.quiz_data)
    
    st.progress((current_index) / total_questions)
    st.write(f"Question {current_index + 1} of {total_questions}")
    
    current_quiz = st.session_state.quiz_data[current_index]
    
    question_key = f"submitted_{current_index}"

    with st.form(key=f"quiz_form_{current_index}"):
        st.markdown(f"### Q: {current_quiz['question']}")
        user_choice = st.radio("Choose your answer:", current_quiz['choices'], key=f"choice_{current_index}")
        
        # Disable submit button if already submitted for this question
        submitted = st.form_submit_button("Submit", disabled=st.session_state.get(question_key, False))
        
        if submitted:
            if user_choice == current_quiz['correct_answer']:
                st.session_state.user_scores[st.session_state.username] += 1
                save_scores(st.session_state.user_scores)
                # st.success("✅ Correct!")
            # else:
                # st.error("❌ Incorrect!")
            # st.info(f"💡 Explanation: {current_quiz['explanation']}")
            st.session_state[question_key] = True  # Lock this question
            st.session_state.question_answered = True
            st.rerun()

    
    # with st.form(key=f"quiz_form_{current_index}"):
    #     st.markdown(f"### Q: {current_quiz['question']}")
    #     user_choice = st.radio("Choose your answer:", current_quiz['choices'])
    #     submitted = st.form_submit_button("Submit")
        
    #     if submitted:
    #         if user_choice == current_quiz['correct_answer']:
    #             st.session_state.user_scores[st.session_state.username] += 1
    #             save_scores(st.session_state.user_scores)
    #         #     st.success("✅ Correct!")
    #         # else:
    #         #     st.error("❌ Incorrect!")
    #         # st.info(f"💡 Explanation: {current_quiz['explanation']}")
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

# def quiz_flow():
#     st.title("🧠 STEM Quiz for Kids")
#     st.sidebar.write(f"User: {st.session_state.username}")
#     show_leaderboard()
#     st.markdown(f"**Subject:** {st.session_state.subject} | **Age:** {st.session_state.age}")
    
#     current_index = st.session_state.current_question_index
#     total_questions = len(st.session_state.quiz_data)
    
#     # Progress tracking
#     st.progress((current_index + 1) / total_questions)  # Fixed progress calculation
#     st.write(f"Question {current_index + 1} of {total_questions}")
    
#     # Current question form
#     with st.form(key=f"question_{current_index}", clear_on_submit=True):
#         current_quiz = st.session_state.quiz_data[current_index]
#         st.markdown(f"### Q: {current_quiz['question']}")
#         user_choice = st.radio("Choose your answer:", 
#                              current_quiz['choices'],
#                              key=f"choice_{current_index}")
        
#         submitted = st.form_submit_button("Submit Answer")
        
#         if submitted:
#             if user_choice == current_quiz['correct_answer']:
#                 st.session_state.user_scores[st.session_state.username] += 1
#                 save_scores(st.session_state.user_scores)
#                 st.success("✅ Correct!")
#             else:
#                 st.error("❌ Incorrect!")
#             st.info(f"💡 Explanation: {current_quiz['explanation']}")
#             st.session_state.question_answered = True  # Set navigation flag

#     # Navigation controls (outside form)
#     if st.session_state.get('question_answered', False):
#         st.markdown("---")
#         col1, col2 = st.columns([1, 3])
#         with col1:
#             if current_index < total_questions - 1:
#                 if st.button("Next Question →", 
#                            key=f"next_{current_index}",
#                            type="primary"):
#                     # Atomic state update
#                     st.session_state.current_question_index += 1
#                     del st.session_state.question_answered  # Reset flag
#             else:
#                 st.balloons()
#                 st.success(f"Final Score: {st.session_state.user_scores[st.session_state.username]}/{total_questions}")
#                 if st.button("Start New Quiz", type="primary"):
#                     reset_all()


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
