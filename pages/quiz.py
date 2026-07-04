import streamlit as st
import json
from datetime import datetime
from rag.vectorstore import load_vectorstore
from rag.quiz_generator import generate_mcqs
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Quiz Mode", page_icon="🧠")
st.title("🧠 Quiz Mode")

PROGRESS_FILE = "data/progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"sessions": [], "weak_topics": {}}

def save_progress(data):
    os.makedirs("data", exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Session state init
for key, val in {
    "quiz_questions": [],
    "current_q": 0,
    "score": 0,
    "answers": [],
    "quiz_done": False,
    "answered": False,
    "selected_answer": None,
    "quiz_topic": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Sidebar
with st.sidebar:
    api_key = os.getenv("GOOGLE_API_KEY")    
    topic = st.text_input("Topic to quiz on", placeholder="e.g. Prompt Templates")
    num_q = st.slider("Number of questions", 3, 10, 5)

    if st.button("Generate Quiz 🚀"):
        if not api_key:
            st.error("API key required!")
        elif not topic:
            st.error("Enter a topic!")
        else:
            with st.spinner("Generating quiz from your PDFs..."):
                try:
                    vs = load_vectorstore()
                    questions = generate_mcqs(vs, topic, api_key, num_q)
                    st.session_state.quiz_questions = questions
                    st.session_state.current_q = 0
                    st.session_state.score = 0
                    st.session_state.answers = []
                    st.session_state.quiz_done = False
                    st.session_state.answered = False
                    st.session_state.selected_answer = None
                    st.session_state.quiz_topic = topic
                    st.session_state.progress_saved = False
                    st.success(f"{len(questions)} questions generated!")
                except Exception as e:
                    st.error(f"Error: {e}")

# Quiz UI
questions = st.session_state.quiz_questions

if questions and not st.session_state.quiz_done:
    idx = st.session_state.current_q
    q = questions[idx]

    st.progress((idx) / len(questions))
    st.markdown(f"**Question {idx+1} of {len(questions)}**")
    st.markdown(f"### {q['question']}")

    if not st.session_state.answered:
        selected = st.radio(
            "Choose your answer:",
            options=list(q["options"].keys()),
            format_func=lambda x: f"{x}. {q['options'][x]}",
            key=f"q_{idx}"
        )

        if st.button("Submit Answer"):
            is_correct = selected == q["correct"]
            
            if is_correct:
                st.session_state.score += 1

            st.session_state.answers.append({
                "question": q["question"],
                "selected": selected,
                "correct": q["correct"],
                "is_correct": is_correct,
            })
            st.session_state.answered = True
            st.session_state.selected_answer = selected
            st.rerun()

    else:
        last = st.session_state.answers[-1]
        
        # Show options as disabled
        st.radio(
            "Your answer:",
            options=list(q["options"].keys()),
            format_func=lambda x: f"{x}. {q['options'][x]}",
            index=list(q["options"].keys()).index(last["selected"]),
            disabled=True,
            key=f"q_{idx}_result"
        )

        if last["is_correct"]:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Wrong! Correct answer: {last['correct']}. {q['options'][last['correct']]}")

        st.info(f"💡 {q['explanation']}")

        is_last = idx + 1 == len(questions)
        btn_label = "Submit Quiz ✅" if is_last else "Next Question ➡️"
        
        if st.button(btn_label):
            st.session_state.answered = False
            st.session_state.selected_answer = None
            if is_last:
                st.session_state.quiz_done = True
            else:
                st.session_state.current_q += 1
            st.rerun()

# Results
if st.session_state.quiz_done:
    score = st.session_state.score
    total = len(questions)
    percent = (score / total) * 100

    if not st.session_state.get("progress_saved"):
        progress = load_progress()
        progress["sessions"].append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "topic": st.session_state.quiz_topic,
            "score": score,
            "total": total,
            "percent": percent
        })
        save_progress(progress)
        st.session_state.progress_saved = True   

    st.balloons()
    st.markdown(f"## 🎯 Quiz Complete!")
    st.markdown(f"### Score: {score}/{total} ({percent:.0f}%)")

    if percent >= 80:
        st.success("🔥 Excellent! You're well prepared!")
    elif percent >= 60:
        st.warning("📚 Good effort! Review weak topics.")
    else:
        st.error("😅 Need more practice. Check weak topics below.")

    wrong_answers = [a for a in st.session_state.answers if not a["is_correct"]]
    if wrong_answers:
        st.markdown("### ❌ Questions to Review:")
        for a in wrong_answers:
            st.markdown(f"- {a['question']}")

    # # Save progress
    # progress = load_progress()
    # progress["sessions"].append({
    #     "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    #     "topic": st.session_state.quiz_topic,
    #     "score": score,
    #     "total": total,
    #     "percent": percent
    # })
    # save_progress(progress)

    if st.button("🔁 Try Again"):
        for key in ["quiz_questions", "quiz_done", "answered", "selected_answer"]:
            st.session_state[key] = [] if key == "quiz_questions" else False
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.rerun()