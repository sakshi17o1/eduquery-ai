import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from rag.vectorstore import load_vectorstore

load_dotenv()

st.set_page_config(page_title="Summary Generator", page_icon="📝")
st.title("📝 Summary Generator")

api_key = os.getenv("GOOGLE_API_KEY")

topic = st.text_input("Enter topic to summarize", placeholder="e.g. Prompt Templates, RAG, Chains")

if st.button("Generate Summary 📄"):
    if not topic:
        st.error("Please enter a topic!")
    else:
        with st.spinner("Generating summary..."):
            try:
                vs = load_vectorstore()
                retriever = vs.as_retriever(search_kwargs={"k": 8})
                docs = retriever.invoke(topic)
                context = "\n\n".join([doc.page_content for doc in docs])

                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=api_key,
                    temperature=0.3
                )

                prompt = f"""
Based on the following context from study material, create a clear and concise summary on the topic: "{topic}"

Context:
{context}

Write the summary in these sections:
1. **Overview** — What is it?
2. **Key Concepts** — Main points (bullet points)
3. **How it Works** — Brief explanation
4. **Important Notes** — Things to remember for exam

Keep it student-friendly and exam-focused.
"""
                response = llm.invoke(prompt)
                st.markdown(response.content)

            except Exception as e:
                st.error(f"Error: {e}")