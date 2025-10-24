from django.contrib import admin
from django.urls import path, include 

# Define a lista de padrões de URL para o projeto
urlpatterns = [
    # Rota para o painel de administração do Django
    path('admin/', admin.site.urls),
    
    # Rota que inclui as URLs de autenticação padrão do Django (login, logout, etc.).
    # O Django buscará por templates em 'templates/registration/'
    path('accounts/', include('django.contrib.auth.urls')), 
    
    # Rota para incluir as URLs da sua aplicação principal (notícias).
    # Esta linha faz com que as URLs de 'noticias' sejam a página inicial (root) do projeto.
    path('', include('noticias.urls')), 
]
