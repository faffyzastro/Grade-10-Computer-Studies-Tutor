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
            "1": "Chemistry and Society",
            "2": "Classification of Substances",
            "3": "Atomic Structure",
            "4": "Chemical Bonding",
            "5": "Physical Chemistry"
        },
        "keywords": {
            "introduction to chemistry": "1.1", "branches of chemistry": "1.1", "laboratory": "1.1", "apparatus": "1.1", "careers": "1.1",
            "role of chemistry": "1.2", "environment": "1.2", "society": "1.2",
            "separating mixtures": "2.1", "filtration": "2.1", "distillation": "2.1", "evaporation": "2.1",
            "acids": "2.2", "bases": "2.2", "indicators": "2.2", "ph": "2.2", "neutralization": "2.2",
            "atom": "3.1", "proton": "3.1", "neutron": "3.1", "electron": "3.1",
            "isotope": "3.2", "energy level": "3.2", "orbital": "3.2", "electron configuration": "3.2",
            "periodic table": "3.3", "group": "3.3", "period": "3.3", "valency": "3.3",
            "ionic bonding": "4.1", "electrovalent": "4.1", "ionic": "4.1",
            "covalent bonding": "4.2", "covalent": "4.2", "molecular": "4.2",
            "metallic bonding": "4.3", "metallic": "4.3", "metals": "4.3",
            "gas laws": "5.1", "boyle": "5.1", "charles": "5.1", "diffusion": "5.1",
            "mole concept": "5.2", "molar mass": "5.2", "avogadro": "5.2", "stoichiometry": "5.2"
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
    },
    "pretech": {
        "collection": "pretech_grade9_kicd",
        "strands": {
            "1": "Foundations of Pre-Technical Studies",
            "2": "Communication in Pre-Technical Studies",
            "3": "Materials for Production",
            "4": "Tools and Production",
            "5": "Entrepreneurship"
        },
        "keywords": {
            "raised platform": "1.1", "scaffolding": "1.1", "ladder": "1.1", "fall protection": "1.1",
            "safety on raised": "1.1",
            "hazardous": "1.2", "chemical safety": "1.2", "msds": "1.2", "ppe": "1.2",
            "handling hazardous": "1.2",
            "career": "1.3", "self-exploration": "1.3", "vocational": "1.3",
            "oblique": "2.1", "projection": "2.1", "orthographic": "2.1",
            "visual programming": "2.2", "scratch": "2.2", "block coding": "2.2",
            "wood": "3.1", "timber": "3.1", "plywood": "3.1",
            "waste": "3.2", "recycl": "3.2", "disposal": "3.2",
            "holding tool": "4.1", "clamp": "4.1", "vice": "4.1", "pliers": "4.1",
            "driving tool": "4.2", "hammer": "4.2", "screwdriver": "4.2",
            "project": "4.3", "prototype": "4.3",
            "financial": "5.1", "bank": "5.1", "loan": "5.1", "sacco": "5.1",
            "government": "5.2", "regulation": "5.2", "tax": "5.2", "license": "5.2",
            "business plan": "5.3", "startup": "5.3", "market": "5.3"
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
        print(f"ERROR: Subject '{subject}' not supported. Use 'cs', 'chem', 'bio', or 'pretech'.")
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
    parser.add_argument("--subject", required=True, choices=["cs", "chem", "bio", "pretech"])
    args = parser.parse_args()

    ingest_markdown(args.file, args.subject)