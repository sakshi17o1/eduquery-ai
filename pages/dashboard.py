import streamlit as st
import json
import os

st.set_page_config(page_title="Dashboard", page_icon="📊")
st.title("📊 Progress Dashboard")

PROGRESS_FILE = "data/progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"sessions": [], "weak_topics": {}}

progress = load_progress()
sessions = progress.get("sessions", [])

if not sessions:
    st.info("No quiz sessions yet! Take a quiz first.")
else:
    # Stats
    total_quizzes = len(sessions)
    avg_score = sum(s["percent"] for s in sessions) / total_quizzes
    best_score = max(s["percent"] for s in sessions)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Quizzes", total_quizzes)
    col2.metric("Average Score", f"{avg_score:.0f}%")
    col3.metric("Best Score", f"{best_score:.0f}%")

    st.divider()

    # Score trend
    st.subheader("📈 Score Trend")
    chart_data = {
        "Quiz": [f"#{i+1} {s.get('topic','')}" for i, s in enumerate(sessions)],
        "Score %": [s["percent"] for s in sessions]
    }
    import pandas as pd
    df = pd.DataFrame(chart_data).set_index("Quiz")
    st.line_chart(df)

    st.divider()

    # Session history
    st.subheader("📋 Session History")
    for i, s in enumerate(reversed(sessions)):
        with st.expander(f"Quiz #{total_quizzes - i} — {s.get('topic', 'General')} — {s['date']}"):
            st.write(f"Score: {s['score']}/{s['total']} ({s['percent']:.0f}%)")

    st.divider()

    if st.button("🗑️ Clear History"):
        os.remove(PROGRESS_FILE)
        st.success("History cleared!")
        st.rerun()