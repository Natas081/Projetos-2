from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('opcoes-de-temas/', views.gerenciar_temas_view, name='gerenciar_temas'),

    
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),

    
    path('interesses/', views.gerenciar_interesses, name='pagina_de_interesses'),
    path('interesses/<int:interest_id>/delete/', views.delete_interest_view, name='delete_interest'),
    path('interesses/<int:interest_id>/edit/', views.edit_interest_view, name='edit_interest'),

    
    path('diario/', views.diario_view, name='diario'),
    path('diario/<int:anotacao_id>/delete/', views.deletar_anotacao, name='delete_anotacao'),
    path('diario/<int:anotacao_id>/editar/', views.editar_anotacao, name='editar_anotacao'),  

    
    path('routine/', views.routine_view, name='routine'),
    path('routine/calendario/', views.calendario_leitura_view, name='calendario_leitura_atual'),
    path('routine/calendario/<int:ano>/<int:mes>/', views.calendario_leitura_view, name='calendario_leitura_mes'),

    
    path('streak/', views.streak_page, name='streak'),

    
    path('configuracoes/', views.settings_view, name='settings'),

    
    path('configuracoes/senha/', auth_views.PasswordChangeView.as_view(
        template_name='noticias/auth/password_change.html'
    ), name='password_change'),
    path('configuracoes/senha/ok/', auth_views.PasswordChangeDoneView.as_view(
        template_name='noticias/auth/password_change_done.html'
    ), name='password_change_done'),
    
    path('resumo/', views.resumo_semanal_view, name='resumo_semanal'),

]

