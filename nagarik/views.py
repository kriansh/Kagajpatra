from django.shortcuts import redirect


def set_language(request, code):
    """Persist the chosen language in the session and send the user back."""
    if code in ("en", "ne"):
        request.session["lang"] = code
    return redirect(request.META.get("HTTP_REFERER", "/"))
