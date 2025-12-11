from django.contrib import admin
from django.urls import path, include
from noticias.views import registro_usuario
from django.conf import settings
from django.conf.urls.static import static



from django.contrib.auth import views as auth_views



urlpatterns = [
    path('admin/', admin.site.urls),

    
    path('accounts/registro/', registro_usuario, name='registro'),

    
    
    
    path(
        'accounts/password_change/', 
        auth_views.PasswordChangeView.as_view(
            
            template_name="noticias/auth/password_change.html",
                          
        ), 
        name='password_change'
    ),
    
    
    path(
        'accounts/password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name="noticias/auth/password_change_done.html" 
        ),
        name='password_change_done'
    ),
    

    
    
    
    path('accounts/', include('django.contrib.auth.urls')),

    
    path('', include('noticias.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
