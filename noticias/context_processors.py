# noticias/context_processors.py
from .models import Perfil, CheckIn
from datetime import date

def streak_processor(request):
    """
    Adiciona o perfil do usuário e se ele já fez check-in hoje
    em todas as páginas automaticamente.
    """
    perfil = None
    ja_fez_checkin_hoje = False

    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
        except Perfil.DoesNotExist:
            perfil = None

        if perfil:
            ja_fez_checkin_hoje = CheckIn.objects.filter(
                usuario=request.user,
                data_checkin=date.today()
            ).exists()

    return {
        'perfil': perfil,
        'ja_fez_checkin_hoje': ja_fez_checkin_hoje
    }
