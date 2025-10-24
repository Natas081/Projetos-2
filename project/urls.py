from django.contrib import admin
from django.urls import path, include
# CORREÇÃO CRÍTICA: Esta linha importa a view que faltava!
from noticias.views import registro_usuario 

urlpatterns = [
    # Rota para o painel de administração
    path('admin/', admin.site.urls),
    
    # Rota personalizada para o REGISTRO de usuário
    # Ela usa a view personalizada que você criou (e corrigiu no views.py)
    path('accounts/registro/', registro_usuario, name='registro'),
    
    # Rota Padrão de Autenticação do Django
    # ESSENCIAL: Inclui as views de login, logout e reset de senha padrao do Django.
    path('accounts/', include('django.contrib.auth.urls')),

    # Rota para as URLs da sua aplicação 'noticias'
    path('', include('noticias.urls')), 
]