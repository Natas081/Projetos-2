from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # IMPORTANTE: Inclui as URLs de login/logout, etc.
    # Elas serão acessíveis em /accounts/login/, /accounts/logout/, etc.
    path('accounts/', include('django.contrib.auth.urls')), 
    
    # ESSA LINHA GARANTE QUE AS ROTAS DO 'noticias/urls.py' SEJAM ACESSADAS NA RAIZ (/)
    path('', include('noticias.urls')),
]