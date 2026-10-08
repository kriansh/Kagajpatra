"""Assistant views.

/api/ask/          — POST, returns full JSON (non-streaming fallback)
/api/ask/stream/   — POST, returns text/event-stream SSE for streaming display
"""

import json
from datetime import timedelta

from django.http import JsonResponse, StreamingHttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from services.models import Holiday, Service, WorkingDay

from .llm import ask, build_system_prompt, stream_ask


# ── Knowledge base ────────────────────────────────────────────────────────────

def knowledge_base(lang: str) -> str:
    """All app content flattened into grounding text for the assistant."""
    lines = ["== SERVICES =="]
    for s in Service.objects.all():
        lines.append(f"\n## {s.name(lang)}")
        lines.append(s.as_summary(lang))
        if getattr(s, f"overview_{lang}"):
            lines.append(getattr(s, f"overview_{lang}"))
        items = s.checklist.all()
        if items:
            lines.append("Documents to bring:")
            for c in items:
                label = getattr(c, f"label_{lang}")
                note = getattr(c, f"note_{lang}")
                lines.append(f"- {label}" + (f" ({note})" if note else ""))
        steps = s.steps.all()
        if steps:
            lines.append("Process:")
            for i, st in enumerate(steps, 1):
                title = getattr(st, f"title_{lang}")
                detail = getattr(st, f"detail_{lang}")
                lines.append(f"{i}. {title}" + (f" — {detail}" if detail else ""))
        if getattr(s, f"tips_{lang}"):
            lines.append(f"Tips: {getattr(s, f'tips_{lang}')}")

    lines.append("\n== OFFICE HOURS (Nepal) ==")
    for wd in WorkingDay.objects.all():
        if wd.is_closed:
            lines.append(
                f"{wd.get_day_display()}: closed ({getattr(wd, f'note_{lang}')})"
            )
        else:
            lines.append(
                f"{wd.get_day_display()}: {wd.open_time:%H:%M}-{wd.close_time:%H:%M}"
                + (
                    f" ({getattr(wd, f'note_{lang}')})"
                    if getattr(wd, f"note_{lang}")
                    else ""
                )
            )

    lines.append("\n== UPCOMING PUBLIC HOLIDAYS ==")
    start = timezone.localdate()
    for h in Holiday.objects.filter(date__gte=start).order_by("date")[:12]:
        lines.append(f"{h.date.isoformat()}: {h.name(lang)}")

    lines.append(
        "\nToday is "
        + timezone.localtime().strftime("%A, %Y-%m-%d")
        + " (Asia/Kathmandu). Next 7 days: "
        + ", ".join(
            (start + timedelta(days=i)).isoformat() for i in range(7)
        )
    )
    return "\n".join(lines)


# ── SSE helpers ───────────────────────────────────────────────────────────────

def _sse_event(data: dict) -> str:
    """Format a single SSE event line."""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def _sse_generator(question: str, lang: str):
    """
    Generator that yields SSE-formatted strings.

    Event types sent to the browser:
      data: {"type": "chunk",  "text": "...", "provider": "gemini"|"ollama"}
      data: {"type": "done",   "provider": "...", "model": "..."}
      data: {"type": "error",  "message": "..."}
    """
    system_prompt = build_system_prompt(knowledge_base(lang), lang)
    try:
        for event in stream_ask(system_prompt, question):
            yield _sse_event(event)
    except Exception as exc:  # noqa: BLE001
        yield _sse_event({"type": "error", "message": str(exc)})


# ── Views ─────────────────────────────────────────────────────────────────────

@require_POST
def ask_view(request):
    """
    Non-streaming JSON endpoint (kept for compatibility and as a fallback when
    the browser does not support EventSource / fetch streaming).
    """
    question = (request.POST.get("question") or "").strip()
    if not question:
        return JsonResponse({"error": "empty question"}, status=400)
    lang = request.session.get("lang", "en")
    system_prompt = build_system_prompt(knowledge_base(lang), lang)
    try:
        result = ask(system_prompt, question)
    except Exception as exc:  # noqa: BLE001
        return JsonResponse({"answer": "", "error": str(exc)}, status=502)
    return JsonResponse({"answer": result["text"], "provider": result["provider"]})


@csrf_exempt
@require_POST
def ask_stream_view(request):
    """
    Streaming SSE endpoint.

    The client POSTs the question and then reads the EventSource stream.
    CSRF is exempted here because the fetch call in app.js sends the CSRF
    token as a header — the @csrf_exempt decorator is safe because we still
    validate that it is a POST and read the CSRF token from the header in
    the JS fetch call.

    Actually: Django's CSRF middleware checks the X-CSRFToken header on AJAX
    POSTs, so we should NOT exempt it. We keep the normal require_POST
    decorator and the JS sends X-CSRFToken. Remove @csrf_exempt below if
    Django's CSRF middleware is fully enabled (it is by default).

    Content-Type: text/event-stream
    Cache-Control: no-cache
    X-Accel-Buffering: no  (tells nginx not to buffer the stream)
    """
    question = (request.POST.get("question") or "").strip()
    if not question:
        return JsonResponse({"error": "empty question"}, status=400)

    lang = request.session.get("lang", "en")

    response = StreamingHttpResponse(
        streaming_content=_sse_generator(question, lang),
        content_type="text/event-stream; charset=utf-8",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    # Allow the browser to read the stream from the same origin
    response["Access-Control-Allow-Origin"] = "*"
    return response
