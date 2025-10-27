from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from datetime import date, timedelta
from .models import Interest, Noticia, Perfil, CheckIn, Goal

# -----------------------------
# PÁGINAS PRINCIPAIS
# -----------------------------
def home(request):
    noticias = Noticia.objects.all().order_by('-id')[:5]
    return render(request, 'noticias/home.html', {"noticias": noticias})

# -----------------------------
# ROTINA DE INTERESSES COM METAS
# -----------------------------
def routine_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "Você precisa estar logado para acessar a rotina.")
        return redirect('login')

    # Pega interesses do usuário
    interests = Interest.objects.filter(user=request.user).order_by('name')

    # Pega metas semanais ativas
    week_start = Goal.get_start_of_week()
    goals = Goal.objects.filter(user=request.user, weekStartDate=week_start).select_related('interest')

    # Atualiza progresso de uma meta se botão clicado
    if request.method == 'POST':
        goal_id = request.POST.get('goal_id')
        try:
            goal = Goal.objects.get(id=goal_id, user=request.user)
            if goal.currentProgress < goal.targetFrequency:
                goal.currentProgress += 1
                goal.save()
                messages.success(request, f'Progresso atualizado para "{goal.interest.name}" ({goal.currentProgress}/{goal.targetFrequency}).')
            else:
                messages.info(request, f'Você já completou a meta de "{goal.interest.name}" esta semana!')
        except Goal.DoesNotExist:
            messages.error(request, 'Meta não encontrada.')
        return redirect('routine')  # Evita repost do formulário

    return render(request, 'noticias/routine.html', {
        'interests': interests,
        'goals': goals
    })

# -----------------------------
# AUTENTICAÇÃO
# -----------------------------
def registro_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Conta criada com sucesso para {user.username}!')
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'noticias/registration/registro.html', {'form': form})

def login_usuario(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    else:
        form = AuthenticationForm()
    return render(request, 'noticias/registration/login.html', {'form': form})

def logout_usuario(request):
    logout(request)
    messages.info(request, 'Você saiu da conta.')
    return redirect('login')

# -----------------------------
# INTERESSES
# -----------------------------
def gerenciar_interesses(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Você precisa estar logado para gerenciar interesses.')
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('name')
        target_frequency = request.POST.get('target_frequency')  # leituras por semana

        if name:
            interest, created = Interest.objects.get_or_create(user=request.user, name=name)
            messages.success(request, f'Interesse "{name}" adicionado!')

            # Cria meta semanal se informado
            if target_frequency and target_frequency.isdigit():
                week_start = Goal.get_start_of_week()
                Goal.objects.create(
                    user=request.user,
                    interest=interest,
                    targetFrequency=int(target_frequency),
                    currentProgress=0,
                    weekStartDate=week_start
                )
                messages.success(request, f'Meta semanal criada: {target_frequency} leituras.')

            return redirect('pagina_de_interesses')

    interests_list = Interest.objects.filter(user=request.user).order_by('name')
    return render(request, 'noticias/interesses.html', {'interests_list': interests_list})

def delete_interest_view(request, interest_id):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            interest = Interest.objects.get(id=interest_id, user=request.user)
            interest.delete()
            messages.success(request, 'Interesse deletado!')
        except Interest.DoesNotExist:
            messages.error(request, 'Interesse não encontrado.')
    return redirect('pagina_de_interesses')

# -----------------------------
# STREAK
# -----------------------------
def streak_page(request):
    if not request.user.is_authenticated:
        messages.error(request, "Você precisa estar logado para acessar sua sequência.")
        return redirect('login')

    perfil = request.user.perfil
    hoje = date.today()
    ontem = hoje - timedelta(days=1)

    ja_fez = CheckIn.objects.filter(usuario=request.user, data_checkin=hoje).exists()

    if request.method == 'POST' and not ja_fez:
        CheckIn.objects.create(usuario=request.user)
        if perfil.ultima_leitura == ontem:
            perfil.leitura_streak += 1
        else:
            perfil.leitura_streak = 1
        perfil.ultima_leitura = hoje
        perfil.save()
        messages.success(request, "Check-in confirmado com sucesso! 🔥")
        return redirect('streak')

    return render(request, 'noticias/streak.html', {
        "perfil": perfil,
        "ja_fez_checkin_hoje": ja_fez
    })
