from django.conf import settings

from .i18n import get_strings


def app_language(request):
    """Expose the active language (session), UI strings, and language list."""
    lang = request.session.get("lang")
    if lang not in dict(settings.APP_LANGUAGES):
        lang = settings.DEFAULT_LANGUAGE
    return {
        "lang": lang,
        "t": get_strings(lang),
        "app_languages": settings.APP_LANGUAGES,
        "alt_lang": "ne" if lang == "en" else "en",
    }
