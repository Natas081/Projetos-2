from django.urls import path
from . import views

# Define o namespace da aplicação para evitar conflitos de nomes (boa prática)
app_name = 'noticias' 

urlpatterns = [
    # Sua URL da página inicial: Rota vazia '' = raiz do site (/)
    path('', views.home, name='home'),
    
    # Rota de Cadastro/Registro, ligada à View que criamos
    path('accounts/registro/', views.registro_usuario, name='registro'),
    
    # Rotas existentes
    path('rotina/', views.routine_view, name='routine'),
    path('noticia/<int:news_id>/check/', views.check_news_view, name='check_news'),
    path('interesses/', views.gerenciar_interesses, name='pagina_de_interesses'),
    path('interesses/<int:interest_id>/delete/', views.delete_interest_view, name='delete_interest'),
]
