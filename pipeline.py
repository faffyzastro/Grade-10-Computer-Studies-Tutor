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
LOCAL_EMBED_MODEL = "all-MiniLM-L6-v2"

# Map incoming subject keys to their respective collection names
COLLECTION_MAP = {
    "cs": "cs_grade10_kicd",
    "chem": "chem_grade10_kicd",
    "bio": "bio_grade10_kicd"
}

# --- THE 4 MODES (Updated to be Subject-Agnostic) ---
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
    Use this structure:
    - Objectives (based on Bloom's Taxonomy & Learning Outcomes)
    - Introduction (5 mins)
    - Content Delivery & Guided Practice (20 mins)
    - Independent Activity (10 mins)
    - Conclusion/Plenary (5 mins)

    CONTEXT: {context}
    LESSON TOPIC: {question}
    """,

    "teacher": """
    You are a Teacher's Assistant for Grade 10 {subject_name}. 
    Provide the following for the requested topic:
    1. A real-world Kenyan analogy (e.g., using local farming, M-Pesa, household items, or local markets).
    2. Common student misconceptions to watch out for in this topic.
    3. Key 'Board Notes' (The most important summary for students to copy).

    CONTEXT: {context}
    TOPIC: {question}
    """
}


def ask(user_query, manual_mode="auto", subject="cs"):
    """
    The main RAG pipeline function updated for Multi-Subject support.
    """
    # 1. Resolve Collection Name
    collection_name = COLLECTION_MAP.get(subject, "cs_grade10_kicd")
    subject_display_name = {
        "cs": "Computer Studies",
        "chem": "Chemistry",
        "bio": "Biology"
    }.get(subject, "Computer Studies")

    # 2. Connect to Local Vector DB
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=LOCAL_EMBED_MODEL)

    try:
        collection = client.get_collection(name=collection_name, embedding_function=embed_fn)
    except Exception as e:
        return {
            "answer": f"Error: Collection '{collection_name}' not found. Please run ingest.py for this subject.",
            "mode": "error",
            "sources": []
        }

    # 3. Retrieve Relevant Curriculum Chunks
    # We retrieve 4 results now to provide a broader context for the larger science subjects
    results = collection.query(query_texts=[user_query], n_results=4)

    context_text = "\n\n---\n\n".join(results['documents'][0])

    # Extract unique source citations (like) and sub-strand numbers
    raw_sources = [m.get("sub_strand", "General") for m in results['metadatas'][0]]
    sources = list(set(raw_sources))

    # 4. Setup Gemini Brain
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # 5. INTENT DETECTION (The Router)
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

        mode = "tutor"  # default
        for key in TEMPLATES.keys():
            if key in detected_mode:
                mode = key
                break

    # 6. Execute Final Chain
    # We inject the subject_name into the template for better personality
    template = TEMPLATES.get(mode, TEMPLATES["tutor"]).replace("{subject_name}", subject_display_name)

    prompt = PromptTemplate(template=template, input_variables=["context", "question"])
    chain = prompt | llm

    response = chain.invoke({"context": context_text, "question": user_query})

    return {
        "answer": response.content,
        "mode": mode,
        "sources": sources
    }