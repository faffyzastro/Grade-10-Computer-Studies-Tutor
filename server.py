"""
server.py — FastAPI server with true SSE streaming from Gemini.
Run: uvicorn server:app --host 0.0.0.0 --port $PORT
"""

import json
import asyncio
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from pipeline import ask, ask_stream

app = FastAPI(title="ElimuAI — Grade 10 Study Assistant", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── REQUEST MODELS ──────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query:   str
    mode:    Optional[str] = "auto"     # auto | tutor | quiz | lesson | teacher
    subject: Optional[str] = "cs"       # cs | chem | bio


# ─── ROUTES ──────────────────────────────────────────────────────────────────

@app.get("/")
async def serve_ui():
    return FileResponse("index.html")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "ElimuAI"}


# ── Non-streaming (kept as fallback) ─────────────────────────────────────────
@app.post("/ask")
def ask_question(req: QueryRequest):
    result = ask(req.query, req.mode or "auto", req.subject or "cs")
    return result


# ── TRUE streaming endpoint ───────────────────────────────────────────────────
@app.post("/ask/stream")
async def ask_stream_endpoint(req: QueryRequest):
    """
    Server-Sent Events endpoint.
    Tokens arrive from Gemini in real-time and are forwarded immediately
    to the browser — no buffering, no waiting for the full response.

    Each SSE event is JSON:
      {"token": "word ", "done": false}        ← content token
      {"token": "", "done": true,              ← final frame
       "mode": "tutor", "sources": ["1.2"]}
      {"error": "...", "done": true}           ← on error
    """

    async def event_generator():
        loop = asyncio.get_event_loop()

        # ask_stream() is a sync generator — run it in a thread pool
        # so it doesn't block the async event loop.
        # We bridge it by pushing chunks through an asyncio.Queue.
        queue: asyncio.Queue = asyncio.Queue()

        def run_stream():
            try:
                for chunk in ask_stream(
                    req.query,
                    req.mode or "auto",
                    req.subject or "cs",
                ):
                    loop.call_soon_threadsafe(queue.put_nowait, chunk)
            except Exception as e:
                loop.call_soon_threadsafe(
                    queue.put_nowait, {"error": str(e), "done": True}
                )
            finally:
                # Sentinel to signal the generator is finished
                loop.call_soon_threadsafe(queue.put_nowait, None)

        # Start the sync pipeline in a background thread
        loop.run_in_executor(None, run_stream)

        # Forward chunks to the client as SSE as soon as they arrive
        while True:
            chunk = await queue.get()
            if chunk is None:
                break  # Stream finished
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disables nginx buffering on Railway
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
