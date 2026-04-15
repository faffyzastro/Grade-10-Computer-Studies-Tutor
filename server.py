"""
server.py — Multi-Subject FastAPI server for KICD Grade 10 RAG.
Run: uvicorn server:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import FileResponse
import asyncio
import json
from pipeline import ask

app = FastAPI(
    title="Grade 10 Multi-Subject RAG API",
    description="Agentic RAG pipeline supporting Computer Studies, Chemistry, and Biology",
    version="1.1.0",
)

# Enable CORS for local UI interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    mode: Optional[str] = "auto"    # auto | tutor | quiz | lesson | teacher
    subject: Optional[str] = "cs"   # cs | chem | bio

class QueryResponse(BaseModel):
    answer: str
    mode: str
    sources: list[str]

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/ask", response_model=QueryResponse)
def ask_question(req: QueryRequest):
    try:
        # Now passing 'subject' to the pipeline
        result = ask(req.query, req.mode or "auto", req.subject or "cs")
        return QueryResponse(
            answer=result["answer"],
            mode=result["mode"],
            sources=result["sources"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask/stream")
async def ask_stream(req: QueryRequest):
    """Streaming endpoint — updated to be subject-aware."""

    async def event_stream():
        loop = asyncio.get_event_loop()
        try:
            # Passing subject to the executor
            result = await loop.run_in_executor(None, ask, req.query, req.mode or "auto", req.subject or "cs")

            words = result["answer"].split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                data = json.dumps({"token": chunk, "done": False})
                yield f"data: {data}\n\n"
                await asyncio.sleep(0.01)

            final = json.dumps({
                "token": "",
                "done": True,
                "mode": result["mode"],
                "sources": result["sources"],
            })
            yield f"data: {final}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)