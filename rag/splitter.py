from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    langchain_docs = []

    for doc in docs:
        chunks = splitter.split_text(doc["text"])
        for chunk in chunks:
            langchain_docs.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": doc["source"],
                        "page": doc["page"]
                    }
                )
            )

    return langchain_docs
