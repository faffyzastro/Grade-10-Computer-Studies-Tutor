import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# 1. Load your API keys immediately
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# --- CONFIGURATION ---
CHROMA_PATH = "./chroma_db"
LOCAL_EMBED_MODEL = "all-MiniLM-L6-v2"

# --- GLOBAL INITIALIZATION (Loaded once at startup for speed) ---
# This prevents the 500 errors and slowness you were seeing
client = chromadb.PersistentClient(path=CHROMA_PATH)
embed_fn = SentenceTransformerEmbeddingFunction(model_name=LOCAL_EMBED_MODEL)

# Initialize Gemini correctly with the explicit API key
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=API_KEY,
    temperature=0.7
)

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
    Provide: 1. A real-world Kenyan analogy. 2. Common misconceptions. 3. Key 'Board Notes'.

    CONTEXT: {context}
    TOPIC: {question}
    """
}


def ask(user_query, manual_mode="auto", subject="cs"):
    # 1. Resolve Collection Name
    collection_name = COLLECTION_MAP.get(subject, "cs_grade10_kicd")
    subject_display_name = {
        "cs": "Computer Studies",
        "chem": "Chemistry",
        "bio": "Biology"
    }.get(subject, "Computer Studies")

    # 2. Get Collection (Using the global 'client' and 'embed_fn')
    try:
        collection = client.get_collection(name=collection_name, embedding_function=embed_fn)
    except Exception as e:
        return {
            "answer": f"Error: Collection '{collection_name}' not found. Please ensure ingestion completed.",
            "mode": "error",
            "sources": []
        }

    # 3. Retrieve Context
    results = collection.query(query_texts=[user_query], n_results=4)
    context_text = "\n\n---\n\n".join(results['documents'][0])
    sources = list(set([m.get("sub_strand", "General") for m in results['metadatas'][0]]))

    # 4. INTENT DETECTION
    if manual_mode != "auto":
        mode = manual_mode
    else:
        intent_prompt = f"Analyze: '{user_query}'. Classify as: 'tutor', 'quiz', 'lesson', or 'teacher'. Output ONLY the word."
        try:
            detected_mode = llm.invoke(intent_prompt).content.strip().lower()
            mode = next((k for k in TEMPLATES if k in detected_mode), "tutor")
        except:
            mode = "tutor"

    # 5. Execute Final Chain
    template_str = TEMPLATES.get(mode, TEMPLATES["tutor"]).replace("{subject_name}", subject_display_name)
    prompt = PromptTemplate(template=template_str, input_variables=["context", "question"])

    chain = prompt | llm
    response = chain.invoke({"context": context_text, "question": user_query})

    return {
        "answer": response.content,
        "mode": mode,
        "sources": sources
    }