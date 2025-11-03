from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from datetime import date, timedelta
from .models import Interest, Noticia, Perfil, CheckIn, Goal, DiarioEntry
from .models import UserProfile
from .forms import EmailChangeForm, ProfileForm
from django.contrib.auth.decorators import login_required



# -----------------------------
# PÁGINAS PRINCIPAIS
# -----------------------------
def home(request):
    noticias = Noticia.objects.all().order_by('-id')[:5]
    return render(request, 'noticias/home.html', {"noticias": noticias})

# -----------------------------
# DIÁRIO DO APRENDIZADO
# -----------------------------
def diario_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "Você precisa estar logado para acessar o diário.")
        return redirect('login')

    if request.method == "POST":
        texto = request.POST.get("texto")
        if texto.strip() != "":
            DiarioEntry.objects.create(usuario=request.user, texto=texto)
            messages.success(request, "Anotação salva no diário!")
            return redirect('diario')
        else:
            messages.error(request, "Digite algo para salvar sua anotação.")

    anotacoes = DiarioEntry.objects.filter(usuario=request.user).order_by('-data_criacao')
    return render(request, 'noticias/diario.html', {"anotacoes": anotacoes})


def deletar_anotacao(request, anotacao_id):
    if not request.user.is_authenticated:
        messages.error(request, "Você precisa estar logado para fazer isso.")
        return redirect('login')

    anotacao = get_object_or_404(DiarioEntry, id=anotacao_id, usuario=request.user)
    anotacao.delete()
    messages.success(request, "Anotação removida com sucesso!")
    return redirect('diario')


def editar_anotacao(request, anotacao_id):
    if not request.user.is_authenticated:
        messages.error(request, "Você precisa estar logado para editar suas anotações.")
        return redirect('login')

    anotacao = get_object_or_404(DiarioEntry, id=anotacao_id, usuario=request.user)

    if request.method == "POST":
        novo_texto = request.POST.get("texto")
        if novo_texto.strip() == "":
            messages.error(request, "A anotação não pode estar vazia.")
        else:
            anotacao.texto = novo_texto
            anotacao.save()
            messages.success(request, "Anotação atualizada com sucesso! ✅")
            return redirect('diario')

    return render(request, "noticias/editar_anotacao.html", {"anotacao": anotacao})

# -----------------------------
# ROTINA DE INTERESSES COM METAS
# -----------------------------
def routine_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "Você precisa estar logado para acessar a rotina.")
        return redirect('login')

    interests = Interest.objects.filter(user=request.user).order_by('name')
    week_start = Goal.get_start_of_week()
    goals = Goal.objects.filter(user=request.user, weekStartDate=week_start).select_related('interest')

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
        return redirect('routine')

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
            messages.error(request, 'Erro ao cadastrar. Verifique os campos e a senha.')
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



------------------------------------------------------------------------------------------------------------
#PROFILE UPDATE 
------------------------------------------------------------------------------------------------------------

@login_required
def settings_view(request):
    # garante que o usuário tem perfil
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # POST do bloco "Perfil" (display_name + avatar)
        if "save_profile" in request.POST:
            pform = ProfileForm(request.POST, request.FILES, instance=profile)
            eform = EmailChangeForm(user=request.user, instance=request.user)  # deixa o form de e-mail “limpo”
            if pform.is_valid():
                pform.save()
                messages.success(request, "Perfil atualizado.")
                return redirect("settings")

        # POST do bloco "Conta" (trocar e-mail)
        elif "save_email" in request.POST:
            eform = EmailChangeForm(request.POST, user=request.user, instance=request.user)
            pform = ProfileForm(instance=profile)
            if eform.is_valid():
                eform.save()
                messages.success(request, "E-mail alterado com sucesso.")
                return redirect("settings")

    else:
        # GET: só monta os formulários com dados atuais
        pform = ProfileForm(instance=profile)
        eform = EmailChangeForm(user=request.user, instance=request.user)

    return render(request, "noticias/settings.html", {"pform": pform, "eform": eform})


# -----------------------------
# INTERESSES
# -----------------------------
def gerenciar_interesses(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Você precisa estar logado para gerenciar interesses.')
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('name')
        target_frequency = request.POST.get('target_frequency')

        if name:
            interest, created = Interest.objects.get_or_create(user=request.user, name=name)
            messages.success(request, f'Interesse "{name}" adicionado!')

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
