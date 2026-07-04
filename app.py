import streamlit as st
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

from rag.loader import load_pdf_text
from rag.splitter import split_documents
from rag.vectorstore import build_vectorstore, load_vectorstore
from rag.chain import get_rag_chain

st.set_page_config(page_title="EduQuery AI", page_icon="🎓")
st.header("🎓 EduQuery AI — Study Smarter")
st.markdown("""
<style>
/* Gradient Header */
h1 {
    background: linear-gradient(135deg, #6C63FF, #FF6584);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem !important;
}

/* Fade in animation */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.main > div {
    animation: fadeIn 0.5s ease-in-out;
}

/* Answer box styling */
.stExpander {
    border: 1px solid #6C63FF !important;
    border-radius: 12px !important;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #6C63FF, #FF6584) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    transition: transform 0.2s ease !important;
}

.stButton > button:hover {
    transform: scale(1.05) !important;
}

/* Input box */
.stTextInput > div > div > input {
    border: 1px solid #6C63FF !important;
    border-radius: 8px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1A1A2E, #0F0F1A) !important;
    border-right: 1px solid #6C63FF !important;
}
</style>
""", unsafe_allow_html=True)


if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    api_key = os.getenv("GOOGLE_API_KEY")
    
    pdfs = st.file_uploader(
    "Upload PDFs or Word Files",
    accept_multiple_files=True,
    type=["pdf", "docx"]
    )

    if st.button("Process PDFs"):
        with st.spinner("Processing..."):
            docs = load_pdf_text(pdfs)
            chunks = split_documents(docs)
            build_vectorstore(chunks)
            st.success("PDFs indexed successfully")

user_question = st.text_input("Ask a question from the PDFs")

if user_question and api_key:
    vectorstore = load_vectorstore()
    chain = get_rag_chain(vectorstore, api_key)

    result = chain({"query": user_question})

    answer = result["result"]
    sources = result["source_documents"]

    st.session_state.history.append(
        (user_question, answer, sources, datetime.now())
    )

for q, a, s, t in reversed(st.session_state.history):
    st.markdown(f"**🧑 Question:** {q}")
    st.markdown(f"**🤖 Answer:** {a}")

    with st.expander("Sources"):
        for doc in s:
            st.write(f"📄 {doc.metadata['source']} | Page {doc.metadata['page']}")

    st.caption(t.strftime("%Y-%m-%d %H:%M"))
    st.divider()
