from PyPDF2 import PdfReader

def load_pdf_text(pdf_docs):
    documents = []

    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                documents.append({
                    "text": text,
                    "source": pdf.name,
                    "page": i + 1
                })

    return documents
