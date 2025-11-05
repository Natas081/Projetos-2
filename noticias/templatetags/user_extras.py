# noticias/templatetags/user_extras.py
from django import template
register = template.Library()

@register.filter
def initials_from_name(name: str):
    if not name:
        return ""
    parts = str(name).strip().split()
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][:1] + parts[-1][:1]).upper()
