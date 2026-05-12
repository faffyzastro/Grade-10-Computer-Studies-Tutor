"""
pipeline.py — RAG pipeline with TRUE Gemini streaming + round-robin key rotation.

Two public functions:
  ask()        → returns full dict (kept for backward compat / health checks)
  ask_stream() → generator that yields text tokens in real-time from Gemini
"""

import os
import itertools
import threading
import time
from typing import Generator
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# ─── CONFIG ──────────────────────────────────────────────────────────────────

CHROMA_PATH      = "./chroma_db"
LOCAL_EMBED_MODEL = "all-MiniLM-L6-v2"

COLLECTION_NAMES = {
    "cs":      "cs_grade10_kicd",
    "chem":    "chem_grade10_kicd",
    "bio":     "bio_grade10_kicd",
    "pretech": "pretech_grade9_kicd",
}

SUBJECT_LABELS = {
    "cs":      "Computer Studies",
    "chem":    "Chemistry",
    "bio":     "Biology",
    "pretech": "Pre-Technical Studies",
}

SUBJECT_GRADE_LEVEL = {
    "cs":      "Grade 10",
    "chem":    "Grade 10",
    "bio":     "Grade 10",
    "pretech": "Grade 9",
}

# ─── ROUND-ROBIN KEY POOL ────────────────────────────────────────────────────
# .env format:
#   GOOGLE_API_KEY_1=AIza...
#   GOOGLE_API_KEY_2=AIza...
#   GOOGLE_API_KEY_3=AIza...
# Plain GOOGLE_API_KEY also works as a fallback.

def _load_api_keys() -> list[str]:
    keys = []
    i = 1
    while True:
        key = os.getenv(f"GOOGLE_API_KEY_{i}", "").strip()
        if not key:
            break
        keys.append(key)
        i += 1
    plain = os.getenv("GOOGLE_API_KEY", "").strip()
    if plain and plain not in keys:
        keys.append(plain)
    if not keys:
        raise EnvironmentError(
            "No Gemini API keys found. Set GOOGLE_API_KEY or "
            "GOOGLE_API_KEY_1, GOOGLE_API_KEY_2 ... in your .env"
        )
    return keys

API_KEYS   = _load_api_keys()
_key_lock  = threading.Lock()
_key_cycle = itertools.cycle(API_KEYS)

print(f"[KeyPool] {len(API_KEYS)} Gemini API key(s) loaded — round-robin active.")

def _next_key() -> str:
    with _key_lock:
        return next(_key_cycle)

def _is_quota_error(e: Exception) -> bool:
    return any(x in str(e).lower() for x in [
        "429", "quota", "resource_exhausted",
        "rate limit", "too many requests", "ratelimiterror"
    ])

# ─── PROMPT TEMPLATES ────────────────────────────────────────────────────────

TEMPLATES = {
    "tutor": """You are an expert {grade_level} {subject_label} Tutor in Kenya.
Explain concepts clearly using the context. Use bullet points for clarity.
Connect explanations to real Kenyan everyday life (M-Pesa, matatus, hospitals, farms) where helpful.
End with ONE follow-up question to deepen the student's thinking.

CONTEXT: {context}
STUDENT QUESTION: {question}
ANSWER:""",

    "quiz": """You are a Quiz Generator for the KICD 2026 Curriculum ({subject_label}, {grade_level}).
Based on the context, create:
1. Three Multiple Choice Questions (4 options each, mark correct with *)
2. Two Short Answer Questions
3. One Practical / Application Challenge
Include a full Answer Key at the end.

CONTEXT: {context}
TOPIC: {question}
QUIZ:""",

    "lesson": """You are a CBC Lesson Planner for {grade_level} {subject_label} in Kenya.
Create a 40-minute lesson plan:
- Strand & Sub-strand (KICD curriculum)
- Specific Learning Outcomes (Bloom's Taxonomy verbs)
- Core Competencies & Values
- Materials Needed (locally available Kenyan materials)
- Introduction / Hook (5 mins)
- Content Delivery & Guided Practice (20 mins)
- Independent Activity (10 mins)
- Conclusion / Plenary (5 mins)
- Suggested Assessment (CBC rubric language)

CONTEXT: {context}
LESSON TOPIC: {question}
LESSON PLAN:""",

    "teacher": """You are a Teacher's Assistant for {grade_level} {subject_label} in Kenya.
Provide:
1. A real-world Kenyan analogy (M-Pesa, matatus, local markets, hospitals, farms).
2. Common student misconceptions and how to correct them.
3. Key Board Notes — the most important points for students to copy.
4. One quick mid-lesson check-for-understanding question.

CONTEXT: {context}
TOPIC: {question}
TEACHER AID:""",
}

# Shown to the model so the web UI can render diagrams (Mermaid / SVG).
VISUAL_OUTPUT_RULES = """
VISUAL OUTPUT (the student app renders diagrams from your reply):
- When a diagram clarifies the answer (tools, flows, steps), add a fenced Mermaid block using exactly this shape (newline after ```mermaid):
```mermaid
flowchart LR
  A[Label A] --> B[Label B]
```
- Prefer short labels. Use flowchart LR/TB, sequenceDiagram, or mindmap when helpful.
- For very precise technical drawing (e.g. oblique cuboid on a grid, exact angles), Mermaid is often not ideal: give clear step-by-step drawing instructions and/or ASCII. If you still output SVG, use a fenced block ```svg ... ``` containing only SVG markup (no script), one root <svg>...</svg>.
"""

VISUAL_OUTPUT_RULES_PRETECH = """
VISUAL OUTPUT (Pre-Technical is highly visual; use diagrams whenever they help):
- Use ```mermaid fenced blocks for: tool parts (flowchart with labeled nodes), processes, simple comparisons (cavalier vs cabinet as two branches), workshop sequences.
- For oblique projection, grid-based steps, or dimensioned sketches where geometry must be exact, combine: (1) numbered steps the learner draws on squared paper, (2) optional ```svg ... ``` with a single minimal <svg> (no scripts), or ASCII if simpler.
- In quizzes, you may show a diagram then ask "Identify the part labeled X" by using matching labels in the Mermaid/SVG and in the question text.
"""

INTENT_TEMPLATE = """Analyze this user input: "{question}"
Classify it as exactly ONE word: tutor, quiz, lesson, or teacher.
- tutor: asking for an explanation or "what is"
- quiz: asking for a test, questions, or practice
- lesson: asking for a lesson plan or how to teach
- teacher: asking for analogies, board notes, or teaching tips
Output ONLY the single word, nothing else."""

# ─── SHARED RETRIEVAL ────────────────────────────────────────────────────────

def _retrieve(user_query: str, subject: str) -> tuple[str, list[str]]:
    """Fetch relevant chunks from the correct ChromaDB collection."""
    collection_name = COLLECTION_NAMES.get(subject, "cs_grade10_kicd")
    client   = chromadb.PersistentClient(path=CHROMA_PATH)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=LOCAL_EMBED_MODEL)

    try:
        collection = client.get_collection(
            name=collection_name, embedding_function=embed_fn
        )
    except Exception:
        label = SUBJECT_LABELS.get(subject, subject)
        raise ValueError(
            f"The {label} knowledge base hasn't been ingested yet. "
            f"Run: python ingest.py --file your_file.md --subject {subject}"
        )

    results      = collection.query(query_texts=[user_query], n_results=4)
    context_text = "\n\n---\n\n".join(results["documents"][0])
    sources      = list({m.get("sub_strand", "General") for m in results["metadatas"][0]})
    return context_text, sources


def _detect_mode(user_query: str) -> str:
    """Use Gemini (non-streaming) to classify intent. Rotates keys on 429."""
    for attempt in range(len(API_KEYS)):
        key = _next_key()
        try:
            llm    = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=key)
            result = llm.invoke(INTENT_TEMPLATE.format(question=user_query))
            detected = result.content.strip().lower()
            for k in TEMPLATES:
                if k in detected:
                    return k
            return "tutor"
        except Exception as e:
            if _is_quota_error(e):
                time.sleep(0.3)
                continue
            break
    return "tutor"  # safe default


# ─── TRUE STREAMING ──────────────────────────────────────────────────────────

def ask_stream(
    user_query: str,
    manual_mode: str = "auto",
    subject: str = "cs",
) -> Generator[dict, None, None]:
    """
    Generator that yields dicts in real-time:
      {"token": "word ", "done": False}          ← during generation
      {"token": "", "done": True, "mode": ...,   ← final metadata
       "sources": [...]}
      {"error": "message", "done": True}          ← on failure
    """
    subject_label = SUBJECT_LABELS.get(subject, "Computer Studies")
    grade_level   = SUBJECT_GRADE_LEVEL.get(subject, "Grade 10")

    # Step 1 — Retrieve context
    try:
        context_text, sources = _retrieve(user_query, subject)
    except ValueError as e:
        yield {"error": str(e), "done": True}
        return

    # Step 2 — Determine mode
    mode = manual_mode if manual_mode != "auto" else _detect_mode(user_query)

    # Step 3 — Build prompt
    prompt_text = PromptTemplate(
        template=TEMPLATES.get(mode, TEMPLATES["tutor"]),
        input_variables=["context", "question", "subject_label", "grade_level"],
    ).format(
        context=context_text,
        question=user_query,
        subject_label=subject_label,
        grade_level=grade_level,
    )
    if subject == "pretech":
        prompt_text = prompt_text.rstrip() + "\n\n" + VISUAL_OUTPUT_RULES_PRETECH
    else:
        prompt_text = prompt_text.rstrip() + "\n\n" + VISUAL_OUTPUT_RULES

    # Step 4 — Stream tokens from Gemini with key rotation
    streamed_ok = False
    for attempt in range(len(API_KEYS)):
        key = _next_key()
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=key,
                streaming=True,        # ← enables true token streaming
            )
            # .stream() returns chunks as they arrive from Gemini
            for chunk in llm.stream(prompt_text):
                token = chunk.content
                if token:
                    yield {"token": token, "done": False}

            streamed_ok = True
            break  # success — exit retry loop

        except Exception as e:
            if _is_quota_error(e):
                print(f"[KeyPool] Key ...{key[-6:]} hit 429 during stream. "
                      f"Rotating (attempt {attempt + 1}/{len(API_KEYS)})")
                time.sleep(0.4)
                continue
            # Non-quota error — report immediately
            yield {"error": f"Generation error: {str(e)}", "done": True}
            return

    if not streamed_ok:
        yield {
            "error": "All API keys are rate-limited. Please wait a moment and try again.",
            "done": True,
        }
        return

    # Step 5 — Send final metadata frame
    yield {"token": "", "done": True, "mode": mode, "sources": sources}


# ─── NON-STREAMING FALLBACK (kept for /health and backward compat) ────────────

def ask(user_query: str, manual_mode: str = "auto", subject: str = "cs") -> dict:
    """Collects all stream tokens into one response dict."""
    full_text = []
    mode      = manual_mode
    sources   = []

    for chunk in ask_stream(user_query, manual_mode, subject):
        if chunk.get("error"):
            return {"answer": f"⚠️ {chunk['error']}", "mode": "error", "sources": []}
        if chunk.get("done"):
            mode    = chunk.get("mode", mode)
            sources = chunk.get("sources", sources)
        else:
            full_text.append(chunk.get("token", ""))

    return {"answer": "".join(full_text), "mode": mode, "sources": sources}
