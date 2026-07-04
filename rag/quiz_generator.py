import json
from langchain_google_genai import ChatGoogleGenerativeAI

def generate_mcqs(vectorstore, topic, api_key, num_questions=5):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.7
    )

    # Retrieve relevant chunks from vectorstore
    retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
    docs = retriever.invoke(topic)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""
You are an expert quiz maker. Based on the context below, generate {num_questions} MCQ questions.

Context:
{context}

Rules:
- Each question must have exactly 4 options (A, B, C, D)
- Only one correct answer
- Questions should test understanding, not just memory
- Return ONLY valid JSON, nothing else

Format:
[
  {{
    "question": "What is...?",
    "options": {{
      "A": "option1",
      "B": "option2", 
      "C": "option3",
      "D": "option4"
    }},
    "correct": "A",
    "explanation": "Because..."
  }}
]
"""

    response = llm.invoke(prompt)
    raw = response.content.strip()
    
    # Clean markdown if present
    raw = raw.replace("```json", "").replace("```", "").strip()
    
    return json.loads(raw)