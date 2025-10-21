# Em /noticias/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Sua URL da página inicial
    path('', views.home, name='home'),
    
    # URL da nova página de "Rotina de Interesses"
    path('rotina/', views.routine_view, name='routine'),
    
    # URL que faz o "check" da notícia (Atualiza o Streak E a Meta)
    path('noticia/<int:news_id>/check/', views.check_news_view, name='check_news'),
    
    # URL da página de "Gerenciar Interesses" (Listar e Adicionar)
    path('interesses/', views.gerenciar_interesses, name='pagina_de_interesses'),
    
    # ★ NOVO: URL para APAGAR um interesse específico ★
    path('interesses/<int:interest_id>/delete/', views.delete_interest_view, name='delete_interest'),
]