# project/urls.py
from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    # ESSA LINHA PRECISA EXISTIR!
    path('accounts/', include('django.contrib.auth.urls')), 
    # ESSA LINHA PRECISA EXISTIR E USAR O NOME CORRETO DA SUA APP!
    path('', include('noticias.urls')), 
]