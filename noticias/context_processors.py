# noticias/context_processors.py
from datetime import date
from .models import Perfil, CheckIn, UserProfile  # <-- importa o perfil visual

def streak_processor(request):
    """
    Adiciona ao contexto global:
      - perfil             -> streak e afins
      - ja_fez_checkin_hoje
      - user_profile       -> perfil visual (UserProfile) OU None
      - display_name       -> nome de exibição (fallback = username)
      - avatar_url         -> URL do avatar (ou None)
    """
    perfil = None
    ja_fez_checkin_hoje = False

    user_profile = None
    display_name = None
    avatar_url = None

    if request.user.is_authenticated:
        # Perfil usado no streak
        try:
            perfil = request.user.perfil
        except Perfil.DoesNotExist:
            perfil = None

        if perfil:
            ja_fez_checkin_hoje = CheckIn.objects.filter(
                usuario=request.user,
                data_checkin=date.today()
            ).exists()

        # Perfil visual (nome de exibição + avatar)
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = None

        # Nome exibido: display_name se existir, senão username
        display_name = (
            (user_profile.display_name or "").strip()
            if user_profile else ""
        ) or request.user.username

        # Avatar (caso exista arquivo)
        if user_profile and getattr(user_profile, "avatar", None):
            try:
                avatar_url = user_profile.avatar.url
            except Exception:
                avatar_url = None

    return {
        "perfil": perfil,
        "ja_fez_checkin_hoje": ja_fez_checkin_hoje,
        "user_profile": user_profile,
        "display_name": display_name,
        "avatar_url": avatar_url,
    }

