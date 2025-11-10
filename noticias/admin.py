# Em noticias/admin.py

from django.contrib import admin
from .models import Categoria, Noticia, UserProfile, Perfil, Interest, Goal, DiarioEntry, CheckIn

# Isso "mostra" seus modelos na página de admin
admin.site.register(Categoria)
admin.site.register(Noticia)
admin.site.register(UserProfile)
admin.site.register(Perfil)

# (Opcional, mas bom ter)
# Você pode registrar seus outros modelos também, se quiser
admin.site.register(Interest)
admin.site.register(Goal)
admin.site.register(DiarioEntry)
admin.site.register(CheckIn)