import argparse
import json
import os
from pathlib import Path

# LangChain and Vector DB imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

# --- GLOBAL CONFIGURATION ---
CHROMA_PATH = "./chroma_db"
LOCAL_EMBED_MODEL = "all-MiniLM-L6-v2"

# --- SUBJECT-SPECIFIC KNOWLEDGE MAPS (Derived from KICD Markdowns) ---
KNOWLEDGE_MAPS = {
    "cs": {
        "collection": "cs_grade10_kicd",
        "strands": {
            "1": "Foundation of Computer Studies",
            "2": "Computer Networking",
            "3": "Software Development",
            "4": "ICT and Society"
        },
        "keywords": {
            "evolution": "1.1", "generation": "1.1", "abacus": "1.1", "pascaline": "1.1",
            "architecture": "1.2", "von neumann": "1.2", "cpu": "1.2",
            "input": "1.3", "output": "1.3", "scanner": "1.3", "printer": "1.3",
            "storage": "1.4", "ram": "1.4", "rom": "1.4", "ssd": "1.4",
            "system software": "1.5", "operating system": "1.5", "os": "1.5",
            "setup": "1.6", "ergonomics": "1.6", "safety": "1.6",
            "data communication": "2.1", "protocol": "2.1", "simplex": "2.1",
            "transmission media": "2.2", "fibre": "2.2", "wireless": "2.2",
            "network elements": "2.3", "router": "2.3", "switch": "2.3", "lan": "2.3",
            "topology": "2.4", "star": "2.4", "mesh": "2.4",
            "internet": "2.5", "www": "2.5", "cloud": "2.5",
            "programming": "3.1", "paradigm": "3.1", "compiler": "3.1",
            "pdlc": "3.2", "algorithm": "3.2", "flowchart": "3.2",
            "variable": "3.3", "operator": "3.3", "data type": "3.3", "python": "3.3",
            "control structure": "3.4", "if statement": "3.4", "loop": "3.4",
            "data structure": "3.5", "list": "3.5", "array": "3.5",
            "function": "3.6", "module": "3.6",
            "cybersecurity": "4.1", "netiquette": "4.1",
            "e-learning": "4.2", "telemedicine": "4.2", "digital divide": "4.2",
            "emerging technology": "4.3", "ai": "4.3", "blockchain": "4.3"
        }
    },
    "chem": {
        "collection": "chem_grade10_kicd",
        "strands": {
            "1": "Inorganic Chemistry",
            "2": "Physical Chemistry"
        },
        "keywords": {
            "branches of chemistry": "1.1", "laboratory": "1.1", "apparatus": "1.1",
            "atom": "1.2", "isotope": "1.2", "energy level": "1.2", "orbital": "1.2",
            "periodic table": "1.3", "group": "1.3", "period": "1.3", "valency": "1.3",
            "chemical bond": "1.4", "ionic": "1.4", "covalent": "1.4", "metallic": "1.4",
            "gas laws": "2.1", "boyle": "2.1", "charles": "2.1", "diffusion": "2.1",
            "mole concept": "2.2", "molar mass": "2.2", "avogadro": "2.2", "stoichiometry": "2.2"
        }
    },
    "bio": {
        "collection": "bio_grade10_kicd",
        "strands": {
            "1": "Introduction to Biology",
            "2": "Human Physiology",
            "3": "Reproduction in Humans"
        },
        "keywords": {
            "mrs gren": "1.1", "botany": "1.1", "zoology": "1.1",
            "classification": "1.2", "binomial nomenclature": "1.2", "taxonomic": "1.2",
            "cell": "1.3", "microscope": "1.3", "magnification": "1.3",
            "chemicals of life": "1.4", "carbohydrates": "1.4", "proteins": "1.4", "food test": "1.4",
            "digestive": "2.1", "enzymes": "2.1", "villi": "2.1", "balanced diet": "2.1",
            "circulatory": "2.2", "heart": "2.2", "artery": "2.2", "blood": "2.2",
            "respiratory": "2.3", "breathing": "2.3", "alveoli": "2.3", "trachea": "2.3",
            "reproductive system": "3.1", "fertilization": "3.1", "gametes": "3.1",
            "reproductive health": "3.2", "rti": "3.2", "syphilis": "3.2",
            "family planning": "3.3", "contraceptive": "3.3", "abstinence": "3.3"
        }
    }
}


def detect_sub_strand(text: str, subject: str) -> str:
    text_lower = text.lower()
    subject_map = KNOWLEDGE_MAPS.get(subject, {}).get("keywords", {})
    # Prioritize specific sub-strand keywords
    for keyword, sub_strand in subject_map.items():
        if keyword in text_lower:
            return sub_strand
    return "general"


def ingest_markdown(file_path: str, subject: str):
    if subject not in KNOWLEDGE_MAPS:
        print(f"ERROR: Subject '{subject}' not supported. Use 'cs', 'chem', or 'bio'.")
        return

    config = KNOWLEDGE_MAPS[subject]
    collection_name = config["collection"]

    # 1. Read File
    print(f"\n[1/4] Reading {subject.upper()} file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            full_text = f.read()
    except FileNotFoundError:
        print(f"ERROR: File '{file_path}' not found.")
        return

    # 2. Split Text - Using Recursive splitting to keep headers with content
    print("[2/4] Splitting text into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n# ", "\n## ", "\n### ", "\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_text(full_text)

    # 3. Create Metadata
    print("[3/4] Generating metadata...")
    metadatas, ids = [], []
    for i, chunk in enumerate(chunks):
        sub_strand = detect_sub_strand(chunk, subject)
        strand = "general" if sub_strand == "general" else sub_strand.split(".")[0]

        metadatas.append({
            "chunk_id": i,
            "strand": strand,
            "strand_name": config["strands"].get(strand, "General"),
            "sub_strand": sub_strand,
            "subject": subject,
            "source": Path(file_path).name
        })
        ids.append(f"{subject}_chunk_{i:04d}")

    # 4. Storage in ChromaDB
    print(f"[4/4] Generating embeddings and storing in '{collection_name}'...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=LOCAL_EMBED_MODEL)

    # Overwrite if exists to ensure clean ingestion
    try:
        client.delete_collection(collection_name)
    except:
        pass

    collection = client.create_collection(
        name=collection_name,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"}
    )

    collection.add(documents=chunks, metadatas=metadatas, ids=ids)

    print(f"\n SUCCESS: {subject.upper()} Ingestion complete!")
    print(f"   Stored {len(chunks)} chunks in '{collection_name}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--subject", required=True, choices=["cs", "chem", "bio"])
    args = parser.parse_args()

    ingest_markdown(args.file, args.subject)