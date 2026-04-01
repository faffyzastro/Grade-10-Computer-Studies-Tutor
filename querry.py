import os
import chromadb
# NEW: Using Local Embedding Function to match ingest.py
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

# Configuration - Must match your ingest.py settings
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "cs_grade10_kicd"
LOCAL_EMBED_MODEL = "all-MiniLM-L6-v2"


def query_curriculum(user_query: str, n_results: int = 3):
    """
    Searches the local Vector DB for the most relevant KICD curriculum chunks.
    """
    # 1. Connect to the local ChromaDB folder
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # 2. Define the Local Embedding Function (No API Key required)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=LOCAL_EMBED_MODEL)

    # 3. Get the collection
    try:
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embed_fn)
    except Exception as e:
        print(f"❌ ERROR: Could not find collection '{COLLECTION_NAME}'. Did you run ingest.py?")
        return

    # 4. Perform the semantic search
    print(f"\n🔍 Searching curriculum for: '{user_query}'...")
    results = collection.query(
        query_texts=[user_query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    # 5. Display the results
    print("\n" + "=" * 60)
    print("TOP RELEVANT KICD CURRICULUM SECTIONS")
    print("=" * 60)

    for i in range(len(results['documents'][0])):
        content = results['documents'][0][i]
        metadata = results['metadatas'][0][i]
        # Similarity score: 1.0 is perfect, 0.0 is completely different
        score = 1 - results['distances'][0][i]

        print(f"\n[RANK {i + 1}] (Similarity: {score:.4f})")
        print(f"📍 STRAND: {metadata['strand']} - {metadata['strand_name']}")
        print(f"📖 SUB-STRAND: {metadata['sub_strand']}")
        print(f"\n--- CONTENT ---\n{content}")
        print("-" * 60)


if __name__ == "__main__":
    # Test Question: Try something specific to the Grade 10 curriculum
    test_question = "Explain the difference between RAM and ROM as per the curriculum."
    query_curriculum(test_question)