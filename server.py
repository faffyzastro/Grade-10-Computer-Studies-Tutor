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
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from pipeline import ask, ask_stream

# Twilio signs the exact webhook URL; behind Railway use the public URL.
_WHATSAPP_MAX_LEN = 3900  # under Twilio/WhatsApp limits; single bubble

# Twilio outbound credentials (for background replies)
_TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
_TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
_TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "").strip()  # e.g. whatsapp:+14155238886


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
            text = text[len(prefix):].strip()
            break
    return text, subject, mode


def _strip_for_whatsapp(s: str) -> str:
    """Rough plain-text for chat; drop fenced code blocks and heavy markdown."""
    s = re.sub(r"```[\s\S]*?```", "[diagram omitted — open elimuai.ke for visuals]", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    return s.strip()


def _twiml_empty() -> Response:
    """Instant empty TwiML — returned to Twilio immediately to avoid timeout."""
    resp = MessagingResponse()
    return Response(content=str(resp), media_type="application/xml")


def _send_whatsapp_outbound(to: str, body: str) -> None:
    """Send the real answer back to the student via Twilio REST API (background)."""
    if not (_TWILIO_ACCOUNT_SID and _TWILIO_AUTH_TOKEN and _TWILIO_WHATSAPP_FROM):
        print("ERROR: Missing TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN / TWILIO_WHATSAPP_FROM env vars.")
        return
    try:
        client = Client(_TWILIO_ACCOUNT_SID, _TWILIO_AUTH_TOKEN)
        client.messages.create(
            from_=_TWILIO_WHATSAPP_FROM,
            to=to,
            body=body[:_WHATSAPP_MAX_LEN],
        )
    except Exception as e:
        print(f"ERROR sending outbound WhatsApp to {to}: {e}")


def _process_and_reply(to: str, query: str, subject: str, mode: str) -> None:
    """
    Runs in a background thread AFTER we've already returned 200 to Twilio.
    Calls the RAG pipeline and sends the answer via outbound Twilio API.
    """
    try:
        result = ask(query, mode, subject)
        answer = result.get("answer") or "No answer returned."
    except Exception as e:
        answer = f"Sorry, something went wrong on my end. Please try again! ({e})"

    plain = _strip_for_whatsapp(answer)
    _send_whatsapp_outbound(to, plain)


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
async def twilio_whatsapp_inbound(request: Request, background_tasks: BackgroundTasks):
    """
    Twilio WhatsApp Sandbox → form-urlencoded POST.

    Strategy: return an EMPTY TwiML response to Twilio immediately (< 1 s),
    then process the RAG pipeline in a background task and send the real
    answer back via the Twilio REST API (outbound message).
    This prevents Twilio's 15-second timeout from killing the request.

    Required env vars:
        TWILIO_ACCOUNT_SID    — from Twilio Console (starts with AC…)
        TWILIO_AUTH_TOKEN     — from Twilio Console
        TWILIO_WHATSAPP_FROM  — e.g. whatsapp:+14155238886 (Sandbox number)

    Optional:
        PUBLIC_WEBHOOK_BASE        — e.g. https://your-host.railway.app
        TWILIO_SKIP_SIGNATURE      — true/1/yes to skip sig check (debug only)
        WHATSAPP_DEFAULT_SUBJECT   — cs | chem | bio | pretech (default: cs)
    """
    form = await request.form()
    params: dict[str, str] = {}
    for key, value in form.multi_items():
        params[str(key)] = str(value)

    # ── Signature validation ──────────────────────────────────────────────
    token = _TWILIO_AUTH_TOKEN
    signature = request.headers.get("X-Twilio-Signature", "") or ""
    url = _twilio_webhook_full_url(request)
    skip_sig = os.getenv("TWILIO_SKIP_SIGNATURE", "").lower() in ("1", "true", "yes")

    if token and not skip_sig:
        if not signature:
            return Response(status_code=403, content="Missing X-Twilio-Signature")
        validator = RequestValidator(token)
        if not validator.validate(url, params, signature):
            return Response(status_code=403, content="Invalid Twilio signature")

    # ── Parse message ─────────────────────────────────────────────────────
    body_text = params.get("Body", "").strip()
    sender    = params.get("From", "").strip()   # e.g. whatsapp:+254700000000

    if not body_text:
        # Can't do background here — just reply inline (fast, no AI needed)
        resp = MessagingResponse()
        resp.message(
            "Send a question about the curriculum. "
            "Optional prefix: cs: chem: bio: pretech: "
            "(example: pretech: What is oblique projection?)"
        )
        return Response(content=str(resp), media_type="application/xml")

    query, subject, mode = _parse_whatsapp_body(body_text)

    if not query:
        resp = MessagingResponse()
        resp.message("I didn't catch a question after the subject prefix. Please try again.")
        return Response(content=str(resp), media_type="application/xml")

    # ── Schedule AI work in background, return instantly to Twilio ────────
    background_tasks.add_task(_process_and_reply, sender, query, subject, mode)
    return _twiml_empty()


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
