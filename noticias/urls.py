from django.urls import path
from . import views

urlpatterns = [
    # Páginas principais
    path('', views.home, name='home'),
    path('rotina/', views.routine_view, name='routine'),

    # Registro e autenticação
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
]
