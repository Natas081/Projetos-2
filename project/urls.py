from django.contrib import admin
from django.urls import path, include
from noticias.views import registro_usuario
from django.conf import settings
from django.conf.urls.static import static

# --- 1. NOVOS IMPORTS ---
# Importa as 'views' de autenticação do Django
from django.contrib.auth import views as auth_views
# Importa seu formulário personalizado do 'noticias'
# ---------------------

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página de cadastro personalizada
    path('accounts/registro/', registro_usuario, name='registro'),

    # --- 2. URLS DE AUTENTICAÇÃO PERSONALIZADAS ---
    # Esta é a URL que 'intercepta' o pedido de alteração de senha.
    # Colocamos ela ANTES do 'include' para ter prioridade.
    path(
        'accounts/password_change/', 
        auth_views.PasswordChangeView.as_view(
            # Aponta para seu template
            template_name="noticias/auth/password_change.html",
            # Usa seu form com CSS
            form_class=CustomPasswordChangeForm               
        ), 
        name='password_change'
    ),
    # Também precisamos da página de 'sucesso' (done) para apontar
    # para o seu template (baseado na sua estrutura de arquivos)
    path(
        'accounts/password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name="noticias/auth/password_change_done.html" 
        ),
        name='password_change_done'
    ),
    # ---------------------------------------------

    # --- 3. MANTEMOS O INCLUDE ORIGINAL ---
    # O Django é inteligente e só vai usar as URLs que 
    # AINDA não definimos (como login, logout, password_reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # Página inicial e rotas da app 'noticias'
    path('', include('noticias.urls')),
]

# servir /media/ em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
