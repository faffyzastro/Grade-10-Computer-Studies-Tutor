import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Load .env file if it exists (local dev only - does nothing on Railway)
load_dotenv()

# --- CONFIGURATION ---
CHROMA_PATH = "./chroma_db"
LOCAL_EMBED_MODEL = "all-MiniLM-L6-v2"

# --- GLOBAL INITIALIZATION ---
# ChromaDB and embeddings are safe to initialize at module level
client = chromadb.PersistentClient(path=CHROMA_PATH)
embed_fn = SentenceTransformerEmbeddingFunction(model_name=LOCAL_EMBED_MODEL)

COLLECTION_MAP = {
    "cs": "cs_grade10_kicd",
    "chem": "chem_grade10_kicd",
    "bio": "bio_grade10_kicd"
}

TEMPLATES = {
    "tutor": """
    You are an expert Grade 10 Tutor in Kenya specializing in {subject_name}. 
    Explain concepts simply using the curriculum context provided. Use bullet points for clarity.
    End your response with ONE follow-up question to help the student think deeper.

    CONTEXT: {context}
    STUDENT QUESTION: {question}
    """,
    "quiz": """
    You are a Quiz Generator for the Grade 10 {subject_name} KICD Curriculum. 
    Based on the context, create:
    1. Three Multiple Choice Questions (MCQs)
    2. Two Short Answer Questions
    3. One Practical Challenge/Experiment
    Provide the Answer Key at the very end.

    CONTEXT: {context}
    TOPIC: {question}
    """,
    "lesson": """
    You are a Professional {subject_name} Lesson Planner. 
    Create a 40-minute lesson plan based on the curriculum design context.
    Structure: Objectives, Introduction (5m), Content Delivery (20m), Activity (10m), Conclusion (5m).

    CONTEXT: {context}
    LESSON TOPIC: {question}
    """,
    "teacher": """
    You are a Teacher's Assistant for Grade 10 {subject_name}. 
    Provide: 1. A real-world Kenyan analogy. 2. Common misconceptions. 3. Key Board Notes.

    CONTEXT: {context}
    TOPIC: {question}
    """
}


def get_llm():
    api_key = (
            os.environ.get("GOOGLE_API_KEY") or
            os.environ.get("GEMINI_API_KEY") or
            os.getenv("GOOGLE_API_KEY") or
            os.getenv("GEMINI_API_KEY")
    )
    if not api_key:
        # Last resort — hardcode temporarily to confirm everything else works
        # REMOVE THIS after confirming
        api_key = "AIzaSyDDzt-YVRQjNZf0KtyyNCzdeugoJ2FPufQ"

    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.7
    )


def ask(user_query, manual_mode="auto", subject="cs"):
    # 1. Resolve Collection Name
    collection_name = COLLECTION_MAP.get(subject, "cs_grade10_kicd")
    subject_display_name = {
        "cs": "Computer Studies",
        "chem": "Chemistry",
        "bio": "Biology"
    }.get(subject, "Computer Studies")

    # 2. Get Collection
    try:
        collection = client.get_collection(name=collection_name, embedding_function=embed_fn)
    except Exception:
        return {
            "answer": f"Error: Collection '{collection_name}' not found. Please ensure ingestion completed.",
            "mode": "error",
            "sources": []
        }

    # 3. Retrieve Context
    results = collection.query(query_texts=[user_query], n_results=4)
    context_text = "\n\n---\n\n".join(results['documents'][0])
    sources = list(set([m.get("sub_strand", "General") for m in results['metadatas'][0]]))

    # 4. Get LLM (reads API key fresh from environment on every call)
    try:
        llm = get_llm()
    except ValueError as e:
        return {
            "answer": str(e),
            "mode": "error",
            "sources": []
        }

    # 5. Intent Detection
    if manual_mode != "auto":
        mode = manual_mode
    else:
        intent_prompt = (
            f"Analyze: '{user_query}'. "
            f"Classify as: 'tutor', 'quiz', 'lesson', or 'teacher'. "
            f"Output ONLY the single word."
        )
        try:
            detected_mode = llm.invoke(intent_prompt).content.strip().lower()
            mode = next((k for k in TEMPLATES if k in detected_mode), "tutor")
        except Exception:
            mode = "tutor"

    # 6. Execute Final Chain
    template_str = TEMPLATES.get(mode, TEMPLATES["tutor"]).replace(
        "{subject_name}", subject_display_name
    )
    prompt = PromptTemplate(template=template_str, input_variables=["context", "question"])
    chain = prompt | llm
    response = chain.invoke({"context": context_text, "question": user_query})

    return {
        "answer": response.content,
        "mode": mode,
        "sources": sources
    }