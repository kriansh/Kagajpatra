from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def bl(context, obj, field):
    """Bilingual field accessor: {% bl service 'name' %} -> name_ne / name_en."""
    lang = context.get("lang", "en")
    value = getattr(obj, f"{field}_{lang}", "") or getattr(obj, f"{field}_en", "")
    return value


@register.filter
def nepali_date(d):
    """Format a date like '१२ अक्टोबर' only for ne? Keep ISO-safe English."""
    if not d:
        return ""
    return d.strftime("%d %b %Y")
