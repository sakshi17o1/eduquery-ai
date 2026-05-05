from langchain_core.prompts import PromptTemplate

PDF_PROMPT = PromptTemplate(
    template="""
You are a PDF-based assistant.

Answer the question using ONLY the context below.
If the answer is not found in the context, say:
"Answer not found in the provided PDF."

Context:
{context}

Question:
{question}

Answer:
""",
    input_variables=["context", "question"]
)
