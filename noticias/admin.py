
from django.contrib import admin
from .models import Categoria, Noticia, UserProfile, Perfil, Interest, Goal, DiarioEntry, CheckIn

admin.site.register(Categoria)
admin.site.register(Noticia)
admin.site.register(UserProfile)
admin.site.register(Perfil)

admin.site.register(Interest)
admin.site.register(Goal)
admin.site.register(DiarioEntry)
admin.site.register(CheckIn)