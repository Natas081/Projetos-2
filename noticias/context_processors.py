
from .models import Perfil, CheckIn, UserProfile
from datetime import date

def streak_processor(request):
    perfil = None
    ja_fez_checkin_hoje = False
    user_profile = None

    if request.user.is_authenticated:
        
        perfil = Perfil.objects.filter(usuario=request.user).first()
        user_profile = UserProfile.objects.filter(user=request.user).first()

        
        if perfil:
            ja_fez_checkin_hoje = CheckIn.objects.filter(
                usuario=request.user, data_checkin=date.today()
            ).exists()

    
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
