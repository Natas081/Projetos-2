from django import template

register = template.Library()

@register.filter
def initials_from_name(value):
    """
    Retorna até 2 iniciais em MAIÚSCULO. Ex: 'Gui Silva' -> 'GS'
    """
    if not value:
        return ""
    parts = str(value).strip().split()
    if not parts:
        return ""
    initials = "".join(p[0] for p in parts[:2]).upper()
    return initials

