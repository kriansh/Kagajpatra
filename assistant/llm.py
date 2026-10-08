"""AI client: hosted Gemma via the Gemini API (streaming SSE), with automatic
fallback to a local Ollama model (streaming NDJSON).

Both providers stream tokens; the Django view consumes the generator and
forwards chunks as Server-Sent Events so the browser can display text as it
arrives.
"""

import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

# ── Gemini ─────────────────────────────────────────────────────────────────
GEMINI_STREAM_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/{model}:streamGenerateContent?alt=sse"
)

# ── Ollama fallback order ───────────────────────────────────────────────────
OLLAMA_FALLBACK_ORDER = ["gemma4:e2b", "gemma4:e4b", "glm4:9b", "qwen3.5:9b"]

# ── System prompt ───────────────────────────────────────────────────────────
SYSTEM_TEMPLATE = """You are Sathi (साथी), a helpful assistant inside an app \
that guides Nepali citizens through government services (birth certificate, \
property tax, citizenship, marriage registration). Answer ONLY from the \
knowledge base below. Keep answers short, simple and kind — many users are \
elderly. Always reply in {language}.

Rules:
- If the answer is not in the knowledge base, say you don't have that \
information and suggest calling the office. Never invent fees, dates or \
requirements.
- Use short sentences. Number lists when listing documents or steps.
- When useful, mention the office name, fee and deadline from the knowledge base.

Knowledge base:
{context}"""


def build_system_prompt(knowledge_base: str, lang: str) -> str:
    language = "Nepali (नेपाली, Devanagari script)" if lang == "ne" else "English"
    return SYSTEM_TEMPLATE.format(language=language, context=knowledge_base)


# ── Shared HTTP helper ───────────────────────────────────────────────────────
def _open_stream(url: str, payload: dict, headers: dict, timeout: float):
    """Open an HTTP POST and return the raw urllib response object (streaming)."""
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    # urllib.request.urlopen returns a file-like; the caller must close it.
    return urllib.request.urlopen(req, timeout=timeout)  # noqa: S310


# ── Gemini streaming ─────────────────────────────────────────────────────────
def stream_gemini(system_prompt: str, question: str):
    """
    Generator that yields text chunks from Gemini's SSE stream.

    Each yielded item is a plain string (a token or small phrase).
    Raises RuntimeError on configuration or HTTP errors.
    """
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured")

    url = GEMINI_STREAM_URL.format(model=settings.GEMINI_MODEL)
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": question}]}],
        "generationConfig": {"temperature": 0.3},
    }

    resp = _open_stream(
        url,
        payload,
        headers={"x-goog-api-key": settings.GEMINI_API_KEY},
        timeout=60,
    )
    try:
        for raw_line in resp:
            line = raw_line.decode("utf-8").rstrip("\n\r")
            if not line.startswith("data:"):
                continue
            data_str = line[5:].strip()
            if not data_str or data_str == "[DONE]":
                continue
            try:
                chunk = json.loads(data_str)
            except json.JSONDecodeError:
                continue
            parts = (
                chunk.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [])
            )
            for part in parts:
                text = part.get("text", "")
                if text:
                    yield text
    finally:
        resp.close()


# ── Ollama streaming ──────────────────────────────────────────────────────────
def _ollama_models() -> list:
    try:
        with urllib.request.urlopen(
            f"{settings.OLLAMA_URL}/api/tags", timeout=3
        ) as r:
            return [m["name"] for m in json.loads(r.read()).get("models", [])]
    except Exception:  # noqa: BLE001
        return []


def stream_ollama(system_prompt: str, question: str):
    """
    Generator that yields (text_chunk, model_name) pairs from Ollama's
    streaming NDJSON chat API.

    The model_name is only included in the first yielded tuple so the caller
    can capture it; subsequent tuples have model_name=None.
    Raises RuntimeError if no model is available.
    """
    available = _ollama_models()
    model = settings.OLLAMA_MODEL
    if model not in available:
        model = next((m for m in OLLAMA_FALLBACK_ORDER if m in available), None)
    if not model:
        raise RuntimeError(f"No local Ollama model available (have: {available})")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        "stream": True,
        "options": {"temperature": 0.3},
    }

    resp = _open_stream(
        f"{settings.OLLAMA_URL}/api/chat",
        payload,
        headers={},
        timeout=180,
    )
    first = True
    try:
        for raw_line in resp:
            line = raw_line.decode("utf-8").strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            text = obj.get("message", {}).get("content", "")
            if text:
                yield (text, model if first else None)
                first = False
            if obj.get("done"):
                break
    finally:
        resp.close()


# ── Unified streaming entry-point ─────────────────────────────────────────────
def stream_ask(system_prompt: str, question: str):
    """
    Generator of SSE-ready dicts:
        {"type": "chunk", "text": "...", "provider": "gemini"|"ollama"}
        {"type": "done",  "provider": "..."}
        {"type": "error", "message": "..."}

    Tries Gemini first; on any failure falls back to Ollama.
    The entire fallback decision happens before the first byte is yielded so
    that we do not mix providers mid-stream.
    """
    # Try Gemini
    gemini_failed = False
    if settings.GEMINI_API_KEY:
        try:
            gen = stream_gemini(system_prompt, question)
            for chunk in gen:
                yield {"type": "chunk", "text": chunk, "provider": "gemini"}
            yield {"type": "done", "provider": "gemini"}
            return
        except Exception as exc:  # noqa: BLE001
            logger.warning("Gemini stream failed (%s); falling back to Ollama", exc)
            gemini_failed = True  # noqa: F841

    # Fallback: Ollama
    try:
        ollama_model = None
        for text, model_name in stream_ollama(system_prompt, question):
            if model_name:
                ollama_model = model_name
            yield {"type": "chunk", "text": text, "provider": "ollama"}
        yield {"type": "done", "provider": "ollama", "model": ollama_model}
    except Exception as exc:  # noqa: BLE001
        logger.error("Ollama stream also failed: %s", exc)
        yield {"type": "error", "message": str(exc)}


# ── Non-streaming helpers (kept for compatibility / tests) ────────────────────
def ask_gemini(system_prompt: str, question: str) -> str:
    """Collect full Gemini response. Used by tests."""
    return "".join(stream_gemini(system_prompt, question))


def ask_ollama(system_prompt: str, question: str):
    """Collect full Ollama response. Used by tests."""
    parts = []
    model = None
    for text, m in stream_ollama(system_prompt, question):
        parts.append(text)
        if m:
            model = m
    return "".join(parts), model


def ask(system_prompt: str, question: str) -> dict:
    """Blocking convenience wrapper. Returns {text, provider[, model]}."""
    try:
        text = ask_gemini(system_prompt, question)
        return {"text": text, "provider": "gemini"}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Gemini unavailable (%s); falling back to Ollama", exc)
    text, model = ask_ollama(system_prompt, question)
    return {"text": text, "provider": "ollama", "model": model}
