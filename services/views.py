from datetime import datetime

from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from nagarik.i18n import STRINGS, get_strings

from .models import Holiday, Service, SiteInfo, WorkingDay

BILINGUAL_FIELDS = ["name", "tagline", "overview", "office", "fee", "timeline", "deadline", "tips"]


def bl(obj, field: str, lang: str) -> str:
    """Pick the active-language value of a bilingual field."""
    return getattr(obj, f"{field}_{lang}", "") or getattr(obj, f"{field}_en", "")


def nepali_weekday(when: datetime) -> int:
    """WorkingDay.day is 0=Sunday .. 6=Saturday (Nepali convention);
    Python weekday() is 0=Monday .. 6=Sunday."""
    return (when.weekday() + 1) % 7


def office_status(now: datetime, lang: str) -> dict:
    """Open / closed / half-day status for right now."""
    strings = get_strings(lang)
    today = WorkingDay.objects.filter(day=nepali_weekday(now)).first()
    if today is None:
        return {"state": "unknown", "label": ""}
    if today.is_closed:
        state = "weekly_holiday" if nepali_weekday(now) == 6 else "closed"
        return {"state": state, "label": strings[state], "day": today}
    current = now.timetz()
    if current < today.open_time or current >= today.close_time:
        return {"state": "closed_now", "label": strings["closed_now"], "day": today}
    if today.is_half_day:
        return {"state": "half_day", "label": strings["half_day"], "day": today}
    return {"state": "open_now", "label": strings["open_now"], "day": today}


def home(request):
    lang = request.session.get("lang", "en")
    strings = get_strings(lang)
    now = timezone.localtime()
    today = now.date()
    idx = nepali_weekday(now)
    holidays = [
        {"h": h, "days": (h.date - today).days}
        for h in Holiday.objects.filter(date__gte=today)[:6]
    ]
    context = {
        "services": [
            {
                "obj": s,
                "slug": s.slug,
                "icon": s.icon,
                "name": bl(s, "name", lang),
                "tagline": bl(s, "tagline", lang),
                "count": s.checklist.count(),
            }
            for s in Service.objects.filter(is_featured=True)
        ],
        "holidays": holidays,
        "working_days": [
            {
                "wd": wd,
                "name": strings["weekdays"][wd.day],
                "hours": (
                    "—"
                    if wd.is_closed
                    else f"{wd.open_time:%H:%M} – {wd.close_time:%H:%M}"
                ),
                "note": getattr(wd, f"note_{lang}"),
            }
            for wd in WorkingDay.objects.all()
        ],
        "site_info": [
            {
                "i": info,
                "label": bl(info, "label", lang),
                "value": bl(info, "value", lang),
            }
            for info in SiteInfo.objects.all()
        ],
        "status": office_status(now, lang),
        "now": now,
        "today_index": idx,
        "today_name": strings["weekdays"][idx],
    }
    return render(request, "home.html", context)


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    lang = request.session.get("lang", "en")
    strings = get_strings(lang)

    groups = {}
    for item in service.checklist.all():
        key = bl(item, "group", lang) or "—"
        groups.setdefault(key, []).append(
            {
                "id": item.id,
                "label": bl(item, "label", lang),
                "note": bl(item, "note", lang),
                "required": item.required,
            }
        )

    context = {
        "sv": {f: bl(service, f, lang) for f in BILINGUAL_FIELDS},
        "slug": service.slug,
        "icon": service.icon,
        "checklist_groups": groups.items(),
        "steps": [
            {"title": bl(s, "title", lang), "detail": bl(s, "detail", lang)}
            for s in service.steps.all()
        ],
        "ask_prefill": strings["ask_prefill"].format(service=bl(service, "name", lang)),
        "all_services": Service.objects.all(),
    }
    return render(request, "service_detail.html", context)
