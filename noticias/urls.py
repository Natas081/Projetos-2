from django.urls import path
from . import views

urlpatterns = [
    # Sua URL da página inicial
    path('', views.home, name='home'),
    
    # URL da nova página de "Rotina de Interesses"
    path('rotina/', views.routine_view, name='routine'),
    
    # URL que faz o "check" da notícia (Atualiza o Streak E a Meta)
    path('noticia/<int:news_id>/check/', views.check_news_view, name='check_news'),
    
    # URL da página de "Gerenciar Interesses" (que você acabou de criar)
    path('interesses/', views.gerenciar_interesses, name='pagina_de_interesses'),
]