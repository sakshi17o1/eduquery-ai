from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from rag.prompt import PDF_PROMPT

def get_rag_chain(vectorstore, api_key):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 5}
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PDF_PROMPT},
        return_source_documents=True
    )

    return chain
