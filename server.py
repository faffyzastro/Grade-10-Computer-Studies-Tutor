"""
server.py — FastAPI server with true SSE streaming from Gemini.
Run: uvicorn server:app --host 0.0.0.0 --port $PORT

WhatsApp (Twilio): POST /whatsapp — set Twilio Sandbox "When a message comes in" to
https://<your-host>/whatsapp and configure TWILIO_AUTH_TOKEN (+ optional PUBLIC_WEBHOOK_BASE).
"""

import json
import asyncio
import os
import re
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from pipeline import ask, ask_stream

# Twilio signs the exact webhook URL; behind Railway use the public URL.
_WHATSAPP_MAX_LEN = 3900  # under Twilio/WhatsApp limits; single bubble


def _twilio_webhook_full_url(request: Request) -> str:
    public = os.getenv("PUBLIC_WEBHOOK_BASE", "").strip().rstrip("/")
    if public:
        return f"{public}/whatsapp"
    proto = request.headers.get("x-forwarded-proto", request.url.scheme or "https")
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    if host:
        return f"{proto}://{host}/whatsapp"
    return str(request.url)


def _parse_whatsapp_body(body: str) -> tuple[str, str, str]:
    """Returns (query, subject, mode). Optional prefix: cs:, chem:, bio:, pretech:"""
    text = (body or "").strip()
    mode = "auto"
    default_subj = os.getenv("WHATSAPP_DEFAULT_SUBJECT", "cs").strip().lower()
    if default_subj not in ("cs", "chem", "bio", "pretech"):
        default_subj = "cs"
    subject = default_subj
    lower = text.lower()
    prefixes = (
        ("pretech:", "pretech"),
        ("pre-tech:", "pretech"),
        ("chem:", "chem"),
        ("chemistry:", "chem"),
        ("bio:", "bio"),
        ("biology:", "bio"),
        ("cs:", "cs"),
        ("computer:", "cs"),
    )
    for prefix, subj in prefixes:
        if lower.startswith(prefix):
            subject = subj
            text = text[len(prefix) :].strip()
            break
    return text, subject, mode


def _strip_for_whatsapp(s: str) -> str:
    """Rough plain-text for chat; drop fenced code blocks and heavy markdown."""
    s = re.sub(r"```[\s\S]*?```", "[diagram omitted — open elimuai.ke for visuals]", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    return s.strip()


def _twiml_message(text: str) -> Response:
    resp = MessagingResponse()
    resp.message(text[:_WHATSAPP_MAX_LEN])
    return Response(content=str(resp), media_type="application/xml")


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
    subject: Optional[str] = "cs"       # cs | chem | bio | pretech


# ─── ROUTES ──────────────────────────────────────────────────────────────────

@app.get("/")
async def serve_ui():
    return FileResponse("index.html")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "ElimuAI"}


@app.get("/whatsapp")
def whatsapp_probe():
    """Sanity check in browser; Twilio sends POST only."""
    return {"status": "ok", "hint": "Twilio should POST here with form fields From, Body, …"}


@app.post("/whatsapp")
async def twilio_whatsapp_inbound(request: Request):
    """
    Twilio WhatsApp Sandbox → form-urlencoded POST.
    Set PUBLIC_WEBHOOK_BASE=https://your-host.railway.app if signature validation fails behind proxy.
    """
    form = await request.form()
    params: dict[str, str] = {}
    for key, value in form.multi_items():
        params[str(key)] = str(value)

    token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    signature = request.headers.get("X-Twilio-Signature", "") or ""
    url = _twilio_webhook_full_url(request)
    skip_sig = os.getenv("TWILIO_SKIP_SIGNATURE", "").lower() in ("1", "true", "yes")

    if token and not skip_sig:
        if not signature:
            return Response(status_code=403, content="Missing X-Twilio-Signature")
        validator = RequestValidator(token)
        if not validator.validate(url, params, signature):
            return Response(status_code=403, content="Invalid Twilio signature")

    body_text = params.get("Body", "").strip()
    if not body_text:
        return _twiml_message(
            "Send a question about the curriculum. "
            "Optional prefix: cs: chem: bio: pretech: (example: pretech: What is oblique projection?)"
        )

    query, subject, mode = _parse_whatsapp_body(body_text)
    if not query:
        return _twiml_message("I did not catch a question after the subject prefix. Try again.")

    try:
        result = ask(query, mode, subject)
        answer = result.get("answer") or "No answer returned."
    except Exception as e:
        answer = f"Sorry, something went wrong. Please try again later. ({e})"

    plain = _strip_for_whatsapp(answer)
    return _twiml_message(plain)


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
