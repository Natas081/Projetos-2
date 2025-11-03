from django.contrib import admin
from django.urls import path, include
from noticias.views import registro_usuario
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página de cadastro personalizada
    path('accounts/registro/', registro_usuario, name='registro'),

    # Sistema de login/logout/pwd reset do Django
    path('accounts/', include('django.contrib.auth.urls')),

    # Página inicial e rotas da app 'noticias'
    path('', include('noticias.urls')),
]

# servir /media/ em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
