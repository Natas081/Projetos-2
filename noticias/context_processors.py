# noticias/context_processors.py
from .models import Perfil, CheckIn, UserProfile
from datetime import date

def streak_processor(request):
    perfil = None
    ja_fez_checkin_hoje = False
    user_profile = None

    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
        except Perfil.DoesNotExist:
            perfil = None
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = None

        if perfil:
            ja_fez_checkin_hoje = CheckIn.objects.filter(
                usuario=request.user, data_checkin=date.today()
            ).exists()

    # nomes para o card do usuário
    display_name = None
    avatar_url = None
    if user_profile:
        display_name = user_profile.display_name or request.user.username
        if user_profile.avatar:
            avatar_url = user_profile.avatar.url

    return {
        'perfil': perfil,
        'ja_fez_checkin_hoje': ja_fez_checkin_hoje,
        'user_profile': user_profile,
        'display_name': display_name or (request.user.username if request.user.is_authenticated else ""),
        'avatar_url': avatar_url,
    }
