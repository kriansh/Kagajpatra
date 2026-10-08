"""AI client: hosted Gemma via the Gemini API, with automatic fallback to
a local Ollama model (gemma4:e2b / whatever is available offline)."""

import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)
# Tried in order when the hosted API is unavailable.
OLLAMA_FALLBACK_ORDER = ["gemma4:e2b", "gemma4:e4b", "glm4:9b", "qwen3.5:9b"]

SYSTEM_TEMPLATE = """You are a helpful assistant inside "Nagarik Sewa", an app that guides
Nepali citizens through government services (birth certificate, property tax, citizenship,
marriage registration). Answer ONLY from the knowledge base below. Keep answers short,
simple and kind — many users are elderly. Always reply in {language}.

Rules:
- If the answer is not in the knowledge base, say you don't have that information and
  suggest calling the office. Never invent fees, dates or requirements.
- Use short sentences. Number lists when listing documents or steps.
- When useful, mention the office name, fee and deadline from the knowledge base.

Knowledge base:
{context}"""


def build_system_prompt(knowledge_base: str, lang: str) -> str:
    language = "Nepali (नेपाली, Devanagari script)" if lang == "ne" else "English"
    return SYSTEM_TEMPLATE.format(language=language, context=knowledge_base)


def _post_json(url: str, payload: dict, headers: dict, timeout: float) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ask_gemini(system_prompt: str, question: str) -> str:
    """Hosted Gemma via the Gemini API. Raises on any failure."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured")
    url = GEMINI_URL.format(model=settings.GEMINI_MODEL)
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": question}]}],
    }
    data = _post_json(
        url,
        payload,
        headers={"x-goog-api-key": settings.GEMINI_API_KEY},
        timeout=20,
    )
    parts = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )
    text = "".join(p.get("text", "") for p in parts).strip()
    if not text:
        raise RuntimeError(f"Empty response from Gemini: {json.dumps(data)[:300]}")
    return text


def _ollama_models() -> list:
    try:
        with urllib.request.urlopen(f"{settings.OLLAMA_URL}/api/tags", timeout=3) as r:
            return [m["name"] for m in json.loads(r.read()).get("models", [])]
    except Exception:
        return []


def ask_ollama(system_prompt: str, question: str) -> str:
    """Local model through Ollama — picks the first available fallback."""
    available = _ollama_models()
    model = settings.OLLAMA_MODEL
    if model not in available:
        model = next((m for m in OLLAMA_FALLBACK_ORDER if m in available), None)
    if not model:
        raise RuntimeError(f"No local model available (have: {available})")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        "stream": False,
        "options": {"temperature": 0.3},
    }
    data = _post_json(f"{settings.OLLAMA_URL}/api/chat", payload, headers={}, timeout=120)
    text = data.get("message", {}).get("content", "").strip()
    if not text:
        raise RuntimeError("Empty response from Ollama")
    return text, model


def ask(system_prompt: str, question: str) -> dict:
    """Try hosted Gemma, fall back to local. Returns {text, provider}."""
    try:
        return {"text": ask_gemini(system_prompt, question), "provider": "gemini"}
    except Exception as exc:  # noqa: BLE001 — any failure means try local
        logger.warning("Gemini unavailable (%s); falling back to local Ollama", exc)
    text, model = ask_ollama(system_prompt, question)
    return {"text": text, "provider": "ollama", "model": model}
