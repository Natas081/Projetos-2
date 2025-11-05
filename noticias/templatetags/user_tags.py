from django import template

register = template.Library()

@register.filter
def initials_from_name(name: str) -> str:
    """
    Retorna duas iniciais a partir de um nome completo.
    - "Guilherme Silvestre Gomes" -> "GG"
    - "admin" -> "AD" (duas primeiras letras)
    - vazio/None -> "?"
    """
    if not name:
        return "?"
    parts = str(name).strip().split()
    if len(parts) == 1:
        base = parts[0][:2]
        return base.upper()
    return (parts[0][0] + parts[-1][0]).upper()
