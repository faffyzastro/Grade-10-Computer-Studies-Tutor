"""
server.py — FastAPI server exposing the RAG pipeline as an HTTP API.
Run: uvicorn server:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
# Updated import: Only importing 'ask' from pipeline.py
from pipeline import ask

app = FastAPI(
    title="Grade 10 CS RAG API",
    description="Agentic RAG pipeline for Longman Grade 10 Computer Studies",
    version="1.0.0",
)

# Enable CORS so your index.html can talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    mode: Optional[str] = "auto"  # auto | tutor | quiz | lesson | teacher

class QueryResponse(BaseModel):
    answer: str
    mode: str
    sources: list[str]

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Grade 10 CS RAG Pipeline",
        "endpoints": ["/ask", "/health", "/docs"],
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/ask", response_model=QueryResponse)
def ask_question(req: QueryRequest):
    try:
        # Calls the 'ask' function in pipeline.py
        result = ask(req.query, req.mode or "auto")
        return QueryResponse(
            answer=result["answer"],
            mode=result["mode"],
            sources=result["sources"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask/stream")
async def ask_stream(req: QueryRequest):
    """Streaming endpoint — streams answer tokens as SSE."""

    async def event_stream():
        # Run the synchronous 'ask' function in a separate thread to keep FastAPI async
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(None, ask, req.query, req.mode or "auto")

            # Stream answer word by word to simulate real-time typing in the UI
            words = result["answer"].split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                data = json.dumps({"token": chunk, "done": False})
                yield f"data: {data}\n\n"
                await asyncio.sleep(0.01) # Small delay for smooth typing effect

            # Final message with metadata (mode and sources)
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