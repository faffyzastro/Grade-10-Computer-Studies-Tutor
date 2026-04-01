import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# 1. Load your API keys
load_dotenv()

# --- CONFIGURATION ---
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "cs_grade10_kicd"
LOCAL_EMBED_MODEL = "all-MiniLM-L6-v2"

# --- THE 4 MODES (Prompt Templates) ---
TEMPLATES = {
    "tutor": """
    You are an expert Grade 10 Computer Studies Tutor in Kenya. 
    Explain concepts simply using the context provided. Use bullet points for clarity.
    End your response with ONE follow-up question to help the student think deeper.

    CONTEXT: {context}
    STUDENT QUESTION: {question}
    """,

    "quiz": """
    You are a Quiz Generator for the KICD Curriculum. 
    Based on the context, create:
    1. Three Multiple Choice Questions (MCQs)
    2. Two Short Answer Questions
    3. One Practical Challenge
    Provide the Answer Key at the very end.

    CONTEXT: {context}
    TOPIC: {question}
    """,

    "lesson": """
    You are a Professional Lesson Planner. 
    Create a 40-minute lesson plan based on the context.
    Use this structure:
    - Objectives (based on Bloom's Taxonomy)
    - Introduction (5 mins)
    - Content Delivery & Guided Practice (20 mins)
    - Independent Activity (10 mins)
    - Conclusion/Plenary (5 mins)

    CONTEXT: {context}
    LESSON TOPIC: {question}
    """,

    "teacher": """
    You are a Teacher's Assistant. 
    Provide the following for the requested topic:
    1. A real-world Kenyan analogy (e.g., using M-Pesa, matatus, or local markets).
    2. Common student misconceptions to watch out for.
    3. Key 'Board Notes' (The most important summary for students to copy).

    CONTEXT: {context}
    TOPIC: {question}
    """
}


def ask(user_query, manual_mode="auto"):
    """
    The main RAG pipeline function called by server.py
    """
    # 1. Connect to Local Vector DB
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=LOCAL_EMBED_MODEL)

    try:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embed_fn)
    except Exception as e:
        return {
            "answer": "Error: Vector database not found. Please run ingest.py first.",
            "mode": "error",
            "sources": []
        }

    # 2. Retrieve Relevant Curriculum Chunks
    results = collection.query(query_texts=[user_query], n_results=3)

    # Extract text and sources (metadata)
    context_text = "\n\n---\n\n".join(results['documents'][0])
    # Extract unique sub-strand numbers for the UI badges
    raw_sources = [m.get("sub_strand", "General") for m in results['metadatas'][0]]
    sources = list(set(raw_sources))

    # 3. Setup Gemini Brain
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # 4. INTENT DETECTION (The Router)
    # If the user selected a specific mode in the HTML sidebar, we skip detection.
    if manual_mode != "auto":
        mode = manual_mode
    else:
        intent_prompt = f"""
        Analyze the user input: "{user_query}"
        Classify it into exactly one of these 4 categories: 'tutor', 'quiz', 'lesson', 'teacher'.
        - If they ask for an explanation or 'what is': 'tutor'
        - If they ask for a test, quiz, or questions: 'quiz'
        - If they mention a lesson plan or 'how to teach': 'lesson'
        - If they ask for analogies, board notes, or teacher tips: 'teacher'
        Output ONLY the category name.
        """
        detected_mode = llm.invoke(intent_prompt).content.strip().lower()

        # Mapping UI names to Template keys
        mode = "tutor"  # default
        for key in TEMPLATES.keys():
            if key in detected_mode:
                mode = key
                break

    # 5. Execute Final Chain
    prompt = PromptTemplate(template=TEMPLATES.get(mode, TEMPLATES["tutor"]), input_variables=["context", "question"])
    chain = prompt | llm

    response = chain.invoke({"context": context_text, "question": user_query})

    # 6. Return the Dictionary format expected by server.py
    return {
        "answer": response.content,
        "mode": mode,
        "sources": sources
    }