from datetime import date, datetime, timedelta

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from services.models import Holiday, Service, WorkingDay

from .llm import ask, build_system_prompt


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
            lines.append(f"{wd.get_day_display()}: closed ({getattr(wd, f'note_{lang}')})")
        else:
            lines.append(
                f"{wd.get_day_display()}: {wd.open_time:%H:%M}-{wd.close_time:%H:%M}"
                + (f" ({getattr(wd, f'note_{lang}')})" if getattr(wd, f"note_{lang}") else "")
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


@require_POST
def ask_view(request):
    question = (request.POST.get("question") or "").strip()
    if not question:
        return JsonResponse({"error": "empty question"}, status=400)
    lang = request.session.get("lang", "en")
    system_prompt = build_system_prompt(knowledge_base(lang), lang)
    try:
        result = ask(system_prompt, question)
    except Exception as exc:  # noqa: BLE001 — surface a friendly message
        return JsonResponse({"answer": "", "error": str(exc)}, status=502)
    return JsonResponse({"answer": result["text"], "provider": result["provider"]})
