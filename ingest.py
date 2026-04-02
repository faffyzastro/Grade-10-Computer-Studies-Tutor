import argparse
import json
import os
from pathlib import Path

# LangChain and Vector DB imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
# NEW: Using Local Embedding Function instead of OpenAI
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv

load_dotenv()

# --- GLOBAL CONFIGURATION ---
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "cs_grade10_kicd"
# We use a proven, lightweight local model
LOCAL_EMBED_MODEL = "all-MiniLM-L6-v2"

STRAND_MAP = {
    "evolution": "1.1", "generation": "1.1", "abacus": "1.1", "vacuum tube": "1.1", "transistor": "1.1",
    "computer architecture": "1.2", "functional organisation": "1.2", "fetch": "1.2", "von neumann": "1.2",
    "input": "1.3", "output": "1.3", "i/o": "1.3", "scanner": "1.3", "printer": "1.3", "qr code": "1.3",
    "storage": "1.4", "ram": "1.4", "rom": "1.4", "hard disk": "1.4", "ssd": "1.4", "flash": "1.4",
    "cpu": "1.5", "central processing": "1.5", "alu": "1.5", "control unit": "1.5", "register": "1.5",
    "operating system": "1.6", "os": "1.6", "windows": "1.6", "linux": "1.6", "booting": "1.6",
    "computer setup": "1.7", "cables": "1.7", "safety": "1.7",
    "data communication": "2.1", "protocol": "2.1", "tcp": "2.1", "osi": "2.1", "bandwidth": "2.1",
    "transmission media": "2.2", "fibre": "2.2", "wireless": "2.2", "multiplexing": "2.2",
    "network elements": "2.3", "router": "2.3", "switch": "2.3", "hub": "2.3", "lan": "2.3", "wan": "2.3",
    "network topology": "2.4", "star": "2.4", "bus topology": "2.4", "ring": "2.4", "mesh": "2.4",
    "programming concept": "3.1", "compiler": "3.1", "interpreter": "3.1", "assembler": "3.1", "paradigm": "3.1",
    "program development": "3.2", "identifier": "3.3", "operator": "3.3", "variable": "3.3", "constant": "3.3", "python": "3.3",
    "control structure": "3.4", "if statement": "3.4", "loop": "3.4", "iteration": "3.4", "selection": "3.4",
    "data structure": "3.5", "array": "3.5", "list": "3.5", "dictionary": "3.5", "tuple": "3.5",
    "function": "3.6", "modular": "3.6", "parameter": "3.6", "return": "3.6", "system software": "1.6", "application software": "1.5",
    "utility": "1.6", "device driver": "1.6", "gui": "1.6", "cli": "1.6",
"bespoke": "1.5", "proprietary": "1.5", "open source": "1.5" , "pascal": "3.1", "writeln": "3.3", "readln": "3.3",
"integer": "3.3", "boolean": "3.3", "assignment": "3.3",
"program heading": "3.1", "begin": "3.1", "end.": "3.1" , "pdlc": "3.2", "algorithm": "3.2", "pseudocode": "3.2",
    "flowchart": "3.2", "dry run": "3.2", "debugging": "3.2",
    "syntax error": "3.2", "logical error": "3.2", "runtime error": "3.2",
    "sequence": "3.4" , "ergonomics": "1.7", "ups": "1.7",
"surge protector": "1.7", "cold boot": "1.7",
"warm boot": "1.7", "peripherals": "1.7", "ports": "1.7", "simplex": "2.1",
    "duplex": "2.1", "network": "2.3", "topology": "2.4", "server": "2.3" , "internet": "2.5", "www": "2.5", "browser": "2.5",
    "url": "2.5", "dns": "2.5", "tcp/ip": "2.5",
    "http": "2.5", "isp": "2.5", "cloud computing": "2.5",
    "cybersecurity": "4.1", "netiquette": "4.1", "e-learning": "4.2", "telemedicine": "4.2", "e-government": "4.2",
    "cybercrime": "4.1", "hacking": "4.1", "piracy": "4.1",
    "digital divide": "4.2", "e-waste": "4.2", "privacy": "4.1",
    "encryption": "4.1", "biometrics": "4.1", "artificial intelligence": "4.3", "machine learning": "4.3",
    "nlp": "4.3", "robotics": "4.3", "iot": "4.3",
    "blockchain": "4.3", "virtual reality": "4.3",
    "augmented reality": "4.3", "big data": "4.3"
}

STRAND_NAMES = {
    "1": "Foundation of Computer Studies",
    "2": "Computer Networking",
    "3": "Software Development",
    "4": "ICT and Society"
}


def detect_sub_strand(text: str) -> str:
    text_lower = text.lower()
    for keyword, sub_strand in STRAND_MAP.items():
        if keyword in text_lower:
            return sub_strand
    return "general"


def detect_strand(sub_strand: str) -> str:
    return "general" if sub_strand == "general" else sub_strand.split(".")[0]


def ingest_markdown(file_path: str):
    # 1. Read File
    print(f"\n[1/4] Reading file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            full_text = f.read()
    except FileNotFoundError:
        print(f"❌ ERROR: File '{file_path}' not found.")
        return
    print(f"       Loaded {len(full_text):,} characters.")

    # 2. Split Text
    print("[2/4] Splitting text into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n# ", "\n## ", "\n### ", "\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_text(full_text)
    print(f"       Created {len(chunks)} text chunks.")

    # 3. Create Metadata
    print("[3/4] Generating CBC-aware metadata...")
    metadatas, ids = [], []
    for i, chunk in enumerate(chunks):
        sub_strand = detect_sub_strand(chunk)
        strand = detect_strand(sub_strand)
        metadatas.append({
            "chunk_id": i,
            "strand": strand,
            "strand_name": STRAND_NAMES.get(strand, "General"),
            "sub_strand": sub_strand,
            "source": Path(file_path).name
        })
        ids.append(f"chunk_{i:04d}")

    # 4. Storage in ChromaDB using LOCAL model
    print(f"[4/4] Generating embeddings locally using '{LOCAL_EMBED_MODEL}'...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # NEW: Local embedding function (No API Key needed here!)
    embed_fn = SentenceTransformerEmbeddingFunction(model_name=LOCAL_EMBED_MODEL)

    try:
        client.delete_collection(COLLECTION_NAME)
    except:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"}
    )

    # Adding chunks to the database
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )

    # Save Manifest
    manifest = {
        "total_chunks": len(chunks),
        "file_source": file_path,
        "collection": COLLECTION_NAME,
        "model": LOCAL_EMBED_MODEL,
        "engine": "local-sentence-transformers"
    }
    with open("ingest_manifest.json", "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"\n✅ SUCCESS: Ingestion complete locally!")
    print(f"   Stored {len(chunks)} chunks in collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    args = parser.parse_args()
    ingest_markdown(args.file)