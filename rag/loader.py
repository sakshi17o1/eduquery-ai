from PyPDF2 import PdfReader
import docx

def load_pdf_text(pdf_docs):
    documents = []

    for file in pdf_docs:
        try:
            name = file.name.lower()
            
            if name.endswith(".pdf"):
                reader = PdfReader(file)
                for i, page in enumerate(reader.pages):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            documents.append({
                                "text": text,
                                "source": file.name,
                                "page": i + 1
                            })
                    except Exception:
                        continue

            elif name.endswith(".docx"):
                doc = docx.Document(file)
                full_text = []
                for para in doc.paragraphs:
                    if para.text.strip():
                        full_text.append(para.text)
                
                # Split into chunks of 50 lines as "pages"
                chunk_size = 50
                for i in range(0, len(full_text), chunk_size):
                    chunk = "\n".join(full_text[i:i+chunk_size])
                    documents.append({
                        "text": chunk,
                        "source": file.name,
                        "page": i // chunk_size + 1
                    })
            else:
                print(f"Unsupported file: {file.name}")
                continue

        except Exception as e:
            print(f"Skipping {file.name}: {e}")
            continue

    return documents