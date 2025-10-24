from django.contrib import admin
from django.urls import path, include
# CORREÇÃO CRÍTICA: Importa a view de registro que está na sua app 'noticias'
from noticias.views import registro_usuario 

urlpatterns = [
    # Rota para o painel de administração
    path('admin/', admin.site.urls),
    
    # Rota personalizada para o REGISTRO de usuário (para o link 'Cadastrar')
    path('accounts/registro/', registro_usuario, name='registro'),
    
    # Rota Padrão de Autenticação do Django (para o link 'Entrar' / 'Login')
    path('accounts/', include('django.contrib.auth.urls')),

    # Rota para a sua app 'noticias' (o arquivo que está no Canvas)
    path('', include('noticias.urls')), 
]

