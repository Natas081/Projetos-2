from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Importações adicionais para autenticação
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
# Importação NECESSÁRIA do modelo Perfil
from .models import Goal, Interest, Noticia, Perfil, CheckIn
from datetime import date, timedelta

# --- FUNÇÃO DE REGISTRO (CADASTRO) ---
def registro_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # --- CORREÇÃO: CRIAÇÃO DO PERFIL ---
            Perfil.objects.create(usuario=user)
            # ------------------------------------
            
            messages.success(request, 'Conta criada com sucesso! Faça login.')
            return redirect('login') 
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/registro.html', {'form': form})
# --------------------------------------

# --- CORREÇÃO FINAL E CRÍTICA ---
# REMOVIDO @login_required daqui.
# Esta view (home) precisa ser pública, senão o base.html (usado pelo login)
# entra em loop de redirecionamento, causando o Erro 500.
def home(request):
    noticias = Noticia.objects.all()
    ja_fez_checkin_hoje = False # Default para usuários deslogados

    # Nós ainda podemos mostrar conteúdo dinâmico se o usuário ESTIVER logado
    if request.user.is_authenticated:
        today = date.today()
        ja_fez_checkin_hoje = CheckIn.objects.filter(usuario=request.user, data_checkin=today).exists()
    
    context = {
        'noticias': noticias,
        'ja_fez_checkin_hoje': ja_fez_checkin_hoje
    }
    return render(request, 'noticias/streak.html', context)

@login_required
def routine_view(request):
    user = request.user
# ... (o resto do seu arquivo 'views.py' continua aqui)
# ... (routine_view, check_news_view, gerenciar_interesses, delete_interest_view)
# ... (certifique-se de que o resto do arquivo esteja igual ao que você tinha)

# ... (colar o resto das suas views aqui) ...
# ...
# ...

# Colar 'routine_view'
    start_of_week = Goal.get_start_of_week()

    Goal.objects.filter(
        user=user,
        weekStartDate__lt=start_of_week
    ).update(
        currentProgress=0,
        weekStartDate=start_of_week
    )
    
    if request.method == 'POST':
        try:
            interest_id = request.POST.get('interest_id')
            frequency = int(request.POST.get('frequency', 0))

            if frequency <= 0:
                messages.error(request, "Frequência inválida, insira um valor positivo")
                return redirect('routine') 

            interest = get_object_or_404(Interest, id=interest_id, user=user)

            Goal.objects.update_or_create(
                user=user,
                interest=interest,
                weekStartDate=start_of_week,
                defaults={'targetFrequency': frequency}
            )
            messages.success(request, f"Meta para '{interest.name}' salva!")

        except (ValueError, TypeError):
            messages.error(request, "Dados inválidos.")
        except Interest.DoesNotExist:
            messages.error(request, "Interesse não encontrado.")
        
        return redirect('routine')

    user_interests = Interest.objects.filter(user=user)

    if not user_interests.exists():
        return render(request, 'noticias/routine.html', {'has_interests': False})

    current_goals = Goal.objects.filter(user=user, weekStartDate=start_of_week)
    context = {
        'has_interests': True,
        'interests_list': user_interests, 
        'goals_list': current_goals,
    }
    return render(request, 'noticias/routine.html', context)


# Colar 'check_news_view'
@login_required
def check_news_view(request, news_id):
    user = request.user
    noticia = get_object_or_404(Noticia, id=news_id)
    today = date.today()
    
    checkin, created = CheckIn.objects.get_or_create(usuario=user, data_checkin=today)
    if created:
        perfil = user.perfil 
        yesterday = today - timedelta(days=1)
        if CheckIn.objects.filter(usuario=user, data_checkin=yesterday).exists():
            perfil.leitura_streak += 1
        else:
            perfil.leitura_streak = 1
        perfil.save()

    if noticia.interest: 
        start_of_week = Goal.get_start_of_week()
        try:
            goal_to_update = Goal.objects.get(
                user=user,
                interest=noticia.interest,
                weekStartDate=start_of_week
            )
            if goal_to_update.currentProgress < goal_to_update.targetFrequency:
                goal_to_update.currentProgress += 1
                goal_to_update.save()
        except Goal.DoesNotExist:
            pass 
            
    return redirect('home')

# Colar 'gerenciar_interesses'
@login_required
def gerenciar_interesses(request):
    user = request.user

    if request.method == 'POST':
        interest_name = request.POST.get('name')
        
        if interest_name:
            interest, created = Interest.objects.get_or_create(
                user=user, 
                name=interest_name.strip()
            )
            if created:
                messages.success(request, f"Interesse '{interest.name}' adicionado!")
            else:
                messages.info(request, f"Interesse '{interest.name}' já existe.")
        else:
            messages.error(request, "O nome do interesse não pode ser vazio.")
        
        return redirect('pagina_de_interesses')

    current_interests = Interest.objects.filter(user=user)
    
    context = {
        'interests_list': current_interests
    }
    return render(request, 'noticias/interesses.html', context)

# Colar 'delete_interest_view'
@login_required
def delete_interest_view(request, interest_id):
    """
    View para apagar um interesse.
    """
    # Busca o interesse, mas garante que ele pertence ao usuário logado
    interest = get_object_or_404(Interest, id=interest_id, user=request.user)
    
    # Usamos POST para segurança (nunca delete com GET)
    if request.method == 'POST':
        interest_name = interest.name
        interest.delete()
        messages.success(request, f"Interesse '{interest_name}' removido com sucesso.")
    
    # Redireciona de volta para a página de gerenciamento
    return redirect('pagina_de_interesses')

