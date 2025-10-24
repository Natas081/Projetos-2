from django.contrib import admin
from django.urls import path, include
from noticias.views import registro_usuario # Importa a view de registro personalizada

urlpatterns = [
    # Rota para o painel de administração
    path('admin/', admin.site.urls),
    
    # Rota personalizada para o REGISTRO de usuário
    # ESSENCIAL: Mapeia o /accounts/registro/ para a sua view
    path('accounts/registro/', registro_usuario, name='registro'),
    
    # Rota Padrão de Autenticação do Django
    # ESSENCIAL: Inclui as views de login, logout e reset de senha padrao do Django.
    path('accounts/', include('django.contrib.auth.urls')),

    # Rota para as URLs da sua aplicação 'noticias'
    path('', include('noticias.urls')), 
]
