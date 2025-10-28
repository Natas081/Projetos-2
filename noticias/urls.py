from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Autenticação
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),

    # Interesses
    path('interesses/', views.gerenciar_interesses, name='pagina_de_interesses'),
    path('interesses/<int:interest_id>/delete/', views.delete_interest_view, name='delete_interest'),

    # Diário do Aprendizado
    path('diario/', views.diario_view, name='diario'),
    path('diario/<int:anotacao_id>/delete/', views.deletar_anotacao, name='delete_anotacao'),
    path('diario/<int:anotacao_id>/editar/', views.editar_anotacao, name='editar_anotacao'),  # <--- ADICIONADO

    # Rotina (METAS SEMANAIS)
    path('routine/', views.routine_view, name='routine'),

    # Streak
    path('streak/', views.streak_page, name='streak'),
]
