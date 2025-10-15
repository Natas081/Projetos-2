from django.urls import path
from . import views

urlpatterns = [
    # URL da página inicial, ex: http://127.0.0.1:8000/
    path('', views.home, name='home'),
    # URL que será chamada pelo formulário para registrar o check-in
    path('registrar-checkin/', views.registrar_checkin, name='registrar_checkin'),
]
