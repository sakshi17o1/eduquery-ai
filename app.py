import streamlit as st
from datetime import datetime
import pandas as pd

from rag.loader import load_pdf_text
from rag.splitter import split_documents
from rag.vectorstore import build_vectorstore, load_vectorstore
from rag.chain import get_rag_chain

st.set_page_config(page_title="PDF RAG Chatbot", page_icon="📚")
st.header("📚 Chat with PDFs (Strict RAG)")

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    api_key = st.text_input("Google Gemini API Key", type="password")

    pdfs = st.file_uploader(
        "Upload PDFs",
        accept_multiple_files=True
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
