from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rotina/', views.routine_view, name='routine'),
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    path('interesses/', views.gerenciar_interesses, name='pagina_de_interesses'),
    path('interesses/<int:interest_id>/delete/', views.delete_interest_view, name='delete_interest'),
    path('streak/', views.streak_page, name='streak'),  # ⚡ corresponde à view correta
]
