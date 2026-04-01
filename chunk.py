import os
import re
from pathlib import Path

# CONFIGURATION
INPUT_FILE = "knowledge_base/markdown/Computer-Studies-new-2026-curriculum-design-for-grade-10-by-KICD.md"
OUTPUT_DIR = Path("knowledge_base/chunks")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def split_by_headers(text):
    """
    Splits the markdown by its highest level headers (e.g., Strands or Chapters).
    """
    # This regex looks for lines starting with # or ##
    # It keeps the header title with the content that follows it.
    pattern = r'(?m)^(#{1,2} .*)$'
    sections = re.split(pattern, text)

    combined_sections = []
    # Re-combine the header with its following content
    for i in range(1, len(sections), 2):
        header = sections[i]
        content = sections[i + 1] if i + 1 < len(sections) else ""
        combined_sections.append(header + content)

    return combined_sections if combined_sections else [text]


def smart_chunker(text, max_words=400, overlap=50):
    """
    If a section is too long, split it into overlapping chunks.
    Otherwise, keep the section as one chunk to preserve context.
    """
    words = text.split()
    if len(words) <= max_words:
        return [text]

    chunks = []
    step = max_words - overlap
    for i in range(0, len(words), step):
        chunk_words = words[i: i + max_words]
        chunks.append(" ".join(chunk_words))
        if i + max_words >= len(words):
            break
    return chunks


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"File not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Split by structural headings first
    sections = split_by_headers(content)

    all_chunks = []
    for section in sections:
        # 2. Break down large sections while keeping them overlapping
        section_chunks = smart_chunker(section)
        all_chunks.extend(section_chunks)

    # 3. Save Chunks
    for idx, chunk in enumerate(all_chunks, 1):
        file_name = OUTPUT_DIR / f"chunk_{idx:03d}.md"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(chunk)

    print(f"Successfully created {len(all_chunks)} structural chunks in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()