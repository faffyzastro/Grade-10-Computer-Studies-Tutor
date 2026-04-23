# ElimuAI — Grade 10 Multi-Subject AI Study Platform


## What is ElimuAI?

ElimuAI is a **Retrieval-Augmented Generation (RAG)** powered AI study platform built specifically for Kenyan Grade 10 students and teachers. It is fully aligned to the **KICD 2026 Competency-Based Curriculum (CBC)** and covers three core subjects:

| Subject | Strands | Collection |
|---------|---------|------------|
| 🖥️ Computer Studies | 4 strands · 14 sub-strands | `cs_grade10_kicd` |
| 🧪 Chemistry | 5 strands · 12 sub-strands | `chem_grade10_kicd` |
| 🌿 Biology | 3 strands · 10 sub-strands | `bio_grade10_kicd` |

Instead of relying on an AI's general knowledge, ElimuAI **first retrieves exact passages** from the official KICD curriculum documents, then uses Google Gemini to generate responses grounded in that specific content — guaranteeing curriculum accuracy.

---

## Features

- **4 AI Modes** — Student Tutor, Quiz Generator, CBC Lesson Planner, Teacher Aid
- **Auto-detect** — AI classifies your question and picks the right mode automatically
- **KICD-aligned answers** — Every response cites which sub-strand it drew from
- **Kenyan context** — Teacher Aid mode gives real-world Kenyan analogies (M-Pesa, local farming, etc.)
- **Mobile responsive** — Full bottom-tab navigation for phones
- **Zero build step** — Single HTML file frontend, no npm or React required

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (index.html)                  │
│         Vanilla JS · Plus Jakarta Sans · Lora            │
└──────────────────────┬──────────────────────────────────┘
                       │ POST /ask  {query, mode, subject}
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  server.py  (FastAPI)                    │
│        /ask · /ask/stream · /health · GET /             │
└──────────────────────┬──────────────────────────────────┘
                       │ ask(query, mode, subject)
                       ▼
┌─────────────────────────────────────────────────────────┐
│                 pipeline.py  (RAG Core)                  │
│                                                          │
│  1. Resolve ChromaDB collection by subject               │
│  2. Embed query → semantic search (top 4 chunks)         │
│  3. Detect intent (auto) or use selected mode            │
│  4. Fill prompt template with context + question         │
│  5. Invoke Gemini 2.0 Flash via LangChain               │
│  6. Return answer + mode + source sub-strands            │
└──────────┬───────────────────────────┬───────────────────┘
           │                           │
           ▼                           ▼
┌──────────────────┐       ┌───────────────────────┐
│   ChromaDB       │       │   Google Gemini API    │
│  ./chroma_db/    │       │   gemini-2.0-flash     │
│                  │       │                        │
│ cs_grade10_kicd  │       │  LangChain wrapper     │
│ chem_grade10_kicd│       │  PromptTemplate chains │
│ bio_grade10_kicd │       └───────────────────────┘
└──────────────────┘
        ▲
        │ python ingest.py --file X.md --subject Y
        │
┌──────────────────┐
│   ingest.py      │
│                  │
│ Read .md → Split │
│ Tag metadata →   │
│ Embed → Store    │
└──────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.13, FastAPI, Uvicorn |
| **AI / LLM** | Google Gemini 2.0 Flash via LangChain |
| **Vector DB** | ChromaDB (persistent, local) |
| **Embeddings** | `all-MiniLM-L6-v2` (Sentence Transformers, 384-dim) |
| **Frontend** | Vanilla HTML/CSS/JS — no framework |
| **Fonts** | Plus Jakarta Sans, Lora, JetBrains Mono |
| **Hosting** | Railway (auto-deploy from GitHub) |
| **Domain** | elimuai.ke via Cloudflare DNS |

---

## Project Structure

```
elimuai/
├── server.py          # FastAPI server — HTTP endpoints
├── pipeline.py        # RAG pipeline — core AI logic
├── ingest.py          # Data pipeline — build ChromaDB
├── index.html         # Complete single-file frontend
├── requirements.txt   # Python dependencies
├── Procfile           # Railway startup command
├── .env               # Local secrets (never committed)
├── .gitignore         # Excludes chroma_db/, .env, venv/
│
├── bio.md             # KICD Biology Grade 10 curriculum
├── chem.md            # KICD Chemistry Grade 10 curriculum
└── Computer-Studies-new-2026-curriculum-design-for-grade-10-by-KICD.md
```

---

## The 4 AI Modes

| Mode | What it does |
|------|-------------|
| 🟣 **Auto-detect** | AI reads your question and picks the best mode automatically |
| 🔵 **Student Tutor** | Explains concepts simply with bullet points. Ends with a follow-up question to deepen thinking |
| 🟡 **Quiz / Assessment** | Generates 3 MCQs + 2 short answers + 1 practical challenge + full answer key |
| 🟢 **CBC Lesson Plan** | Creates a complete 40-minute lesson plan: Objectives → Intro → Content → Activity → Conclusion |
| 🟠 **Teacher Aid** | Provides a real-world Kenyan analogy, common misconceptions to watch for, and key board notes |

---

## Getting Started (Local Development)

### Prerequisites

- Python 3.11+
- A Google AI Studio API key → [aistudio.google.com](https://aistudio.google.com)

### 1. Clone and install

```bash
git clone https://github.com/faffyzastro/elimuai.git
cd elimuai
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### 2. Create your `.env` file

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Ingest the curriculum

```bash
python ingest.py --file bio.md --subject bio
python ingest.py --file chem.md --subject chem
python ingest.py --file "Computer-Studies-new-2026-curriculum-design-for-grade-10-by-KICD.md" --subject cs
```

Each command reads the markdown, chunks it, generates embeddings, and stores everything in `./chroma_db/`.

### 4. Start the server

```bash
uvicorn server:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## Deployment (Railway)

### Environment Variables

Set this in Railway → Variables:

| Variable | Value |
|----------|-------|
| `GOOGLE_API_KEY` | Your Gemini API key from aistudio.google.com |

### Procfile

```
web: python ingest.py --file bio.md --subject bio && python ingest.py --file chem.md --subject chem && python ingest.py --file "Computer-Studies-new-2026-curriculum-design-for-grade-10-by-KICD.md" --subject cs && uvicorn server:app --host 0.0.0.0 --port $PORT
```

> **Note:** Ingestion runs on every deploy because Railway's filesystem resets. This ensures the ChromaDB is always fresh. For faster deploys, attach a Railway persistent volume at `/app/chroma_db`.

### Custom Domain

The domain `elimuai.ke` is managed via Cloudflare DNS:

```
CNAME  @               → 7t7ih4fx.up.railway.app  (proxy OFF)
TXT    _railway-verify → railway-verify=...
```

---

## API Reference

### `POST /ask`

```json
// Request
{
  "query": "Explain the structure of the atom",
  "mode": "auto",       // auto | tutor | quiz | lesson | teacher
  "subject": "chem"     // cs | chem | bio
}

// Response
{
  "answer": "The atom consists of...",
  "mode": "tutor",
  "sources": ["3.1", "3.2"]
}
```

### `POST /ask/stream`

Same request body. Returns Server-Sent Events stream — word by word for a typing effect.

```
data: {"token": "The ", "done": false}
data: {"token": "atom ", "done": false}
data: {"token": "", "done": true, "mode": "tutor", "sources": ["3.1"]}
```

### `GET /health`

```json
{ "status": "healthy" }
```

---

## Curriculum Coverage

### Computer Studies — 4 Strands

<details>
<summary>View all sub-strands</summary>

| Sub-strand | Topic |
|------------|-------|
| 1.1 | Evolution of Computers |
| 1.2 | Computer Architecture & Von Neumann |
| 1.3 | Input & Output Devices |
| 1.4 | Storage Devices |
| 1.5 | System Software & Operating Systems |
| 1.6 | Computer Setup & Ergonomics |
| 2.1 | Data Communication & Protocols |
| 2.2 | Transmission Media |
| 2.3 | Network Elements |
| 2.4 | Network Topologies |
| 2.5 | Internet & Cloud Computing |
| 3.1 | Programming Paradigms |
| 3.2 | PDLC & Algorithms |
| 3.3 | Python — Variables & Data Types |
| 3.4 | Control Structures |
| 3.5 | Data Structures |
| 3.6 | Functions & Modules |
| 4.1 | Cybersecurity & Digital Ethics |
| 4.2 | ICT in Daily Life |
| 4.3 | Emerging Technologies |

</details>

### Chemistry — 5 Strands

<details>
<summary>View all sub-strands</summary>

| Sub-strand | Topic |
|------------|-------|
| 1.1 | Introduction to Chemistry |
| 1.2 | Role of Chemistry in Society |
| 2.1 | Separating Mixtures |
| 2.2 | Acids, Bases & Indicators |
| 3.1 | The Atom |
| 3.2 | Isotopes & Energy Levels |
| 3.3 | Periodic Table |
| 4.1 | Ionic Bonding |
| 4.2 | Covalent Bonding |
| 4.3 | Metallic Bonding |
| 5.1 | Gas Laws |
| 5.2 | Mole Concept & Stoichiometry |

</details>

### Biology — 3 Strands

<details>
<summary>View all sub-strands</summary>

| Sub-strand | Topic |
|------------|-------|
| 1.1 | Meaning & Importance of Biology |
| 1.2 | Classification & Binomial Nomenclature |
| 1.3 | The Cell |
| 1.4 | Chemicals of Life |
| 2.1 | Digestive System |
| 2.2 | Circulatory System |
| 2.3 | Respiratory System |
| 3.1 | Reproductive System |
| 3.2 | Reproductive Health |
| 3.3 | Family Planning |

</details>

---

## How RAG Works

```
User question: "What are the gas laws?"
        │
        ▼
  Embed query → [0.23, -0.41, 0.87, ...] (384 numbers)
        │
        ▼
  ChromaDB cosine similarity search
  → Returns 4 most relevant curriculum chunks
        │
        ▼
  Fill prompt template:
  "You are a Grade 10 Chemistry tutor...
   CONTEXT: [chunk 1] --- [chunk 2] --- ...
   QUESTION: What are the gas laws?"
        │
        ▼
  Gemini 2.0 Flash generates answer
  grounded in the actual KICD curriculum text
        │
        ▼
  Response: answer + mode + source sub-strands
```

> The key insight: Gemini is used as an **explainer**, not a **memoriser**. It explains what the curriculum says, not what it thinks it remembers.

---

## Extending the Platform

### Add a new subject

1. Add entry to `KNOWLEDGE_MAPS` in `ingest.py`
2. Add collection name to `COLLECTION_MAP` in `pipeline.py`
3. Add subject to `SUBJECTS` object in `index.html`
4. Add the markdown file to the repo root
5. Update `Procfile` with the new ingest command
6. Push — Railway redeploys automatically

### Add Grade 11 / 12

The naming convention is built for this. Add collections like `cs_grade11_kicd` and a grade selector to the UI. The pipeline is entirely grade-agnostic.

### Swap the LLM

Because LangChain abstracts the LLM interface, swapping Gemini requires changing only `get_llm()` in `pipeline.py`:

```python
# Switch to Claude
from langchain_anthropic import ChatAnthropic
return ChatAnthropic(model="claude-3-5-haiku-20241022", api_key=api_key)
```

---

## Security Notes

- **Never commit your `.env` file** — it is excluded by `.gitignore`
- **Never hardcode API keys** in source files — use environment variables
- If a key is accidentally committed, delete it from Google AI Studio immediately and generate a new one
- CORS is set to `allow_origins=["*"]` for development — restrict to `https://elimuai.ke` for hardened production

---

## Known Limitations

| Limitation | Description |
|------------|-------------|
| No conversation memory | Each request is stateless — the AI doesn't remember previous messages |
| Ephemeral ChromaDB | Railway resets filesystem on redeploy — ingestion re-runs on each deploy (~3–5 min) |
| First keyword wins | Sub-strand tagging returns the first matching keyword in a chunk |
| No authentication | API is publicly accessible — add rate limiting for high-traffic use |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Douglas Otieno**
- Platform: [elimuai.ke](https://elimuai.ke)
- GitHub: @faffyzastro(https://github.com/faffyzastro)

---

<div align="center">

Built for Kenyan students and teachers · CBC · KICD 2026 · Grade 10

*Powered by Google Gemini · ChromaDB · FastAPI · Railway*

</div>
