from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from .models import CheckIn, Perfil

@login_required
def home(request):
    """
    Exibe a página principal, o prompt de check-in e a sequência do usuário.
    """
    hoje = date.today()
    usuario = request.user
    
    # --- CORREÇÃO AQUI ---
    # Garante que um perfil exista para o usuário logado.
    # Se não existir, ele cria um novo. Se já existir, ele apenas o pega.
    perfil, created = Perfil.objects.get_or_create(usuario=usuario)
    
    # Verifica se o usuário já fez check-in hoje
    checkin_hoje_existe = CheckIn.objects.filter(usuario=usuario, data_checkin=hoje).exists()
    
    contexto = {
        'mostrar_prompt_checkin': not checkin_hoje_existe,
        'streak_atual': perfil.leitura_streak
    }
    return render(request, 'noticias/home.html', contexto)


@login_required
def registrar_checkin(request):
    """
    Processa o clique no botão "SIM" para registrar o check-in.
    """
    if request.method == 'POST':
        hoje = date.today()
        ontem = hoje - timedelta(days=1)
        usuario = request.user
        
        # A mesma lógica de get_or_create aqui para garantir
        perfil, created = Perfil.objects.get_or_create(usuario=usuario)

        # Cenário 3: Verifica se já não existe um check-in para hoje
        if CheckIn.objects.filter(usuario=usuario, data_checkin=hoje).exists():
            messages.warning(request, 'Você já registrou seu check-in hoje.')
            return redirect('home')

        # Cenário 1: Registra o check-in e atualiza o streak
        CheckIn.objects.create(usuario=usuario, data_checkin=hoje)
        
        # Verifica se houve check-in ontem para continuar a sequência
        checkin_ontem_existe = CheckIn.objects.filter(usuario=usuario, data_checkin=ontem).exists()

        if checkin_ontem_existe:
            perfil.leitura_streak += 1 # Continua a sequência
        else:
            perfil.leitura_streak = 1 # Inicia uma nova sequência
        
        perfil.save()
        messages.success(request, 'Check-in registrado com sucesso! Continue assim!')

    # Cenário 2 (implícito): Se não for POST ou se o usuário sair, nada acontece,
    # e na próxima vez a lógica de streak vai reiniciar a contagem.
    return redirect('home')