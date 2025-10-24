from django.urls import path
from . import views  # <-- ESTA LINHA ESTAVA A FALTAR E CAUSAVA O ERRO 500

urlpatterns = [
    # Sua URL da página inicial: Rota vazia '' = raiz do site (/)
    path('', views.home, name='home'),
    
    # Rotas da sua aplicação
    path('rotina/', views.routine_view, name='routine'),
    path('noticia/<int:news_id>/check/', views.check_news_view, name='check_news'),
    path('interesses/', views.gerenciar_interesses, name='pagina_de_interesses'),
    path('interesses/<int:interest_id>/delete/', views.delete_interest_view, name='delete_interest'),
]

