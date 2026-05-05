import os
from langchain_community.vectorstores import FAISS
from rag.embeddings import get_embeddings
FAISS_PATH = "data/faiss_index"

def build_vectorstore(documents):
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(FAISS_PATH)

def load_vectorstore():
    embeddings = get_embeddings()
    return FAISS.load_local(
        FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
