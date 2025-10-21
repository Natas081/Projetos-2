from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Goal, Interest, Noticia, Perfil, CheckIn
from datetime import date, timedelta

# Assumindo que você tenha uma view 'home' em algum lugar
# Se não, você precisará criá-la ou ajustar os redirects
@login_required
def home(request):
    # Lógica da sua página inicial
    noticias = Noticia.objects.all() # Exemplo de busca de notícias
    
    # --- ★ NOVO CÓDIGO ADICIONADO ★ ---
    # Verifica se o usuário já fez check-in hoje
    today = date.today()
    ja_fez_checkin_hoje = CheckIn.objects.filter(usuario=request.user, data_checkin=today).exists()
    
    context = {
        'noticias': noticias,
        'ja_fez_checkin_hoje': ja_fez_checkin_hoje # Passa a variável para o template
    }
    return render(request, 'noticias/streak.html', context)

@login_required
def routine_view(request):
    user = request.user
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


# --- ★ NOVO CÓDIGO ADICIONADO ABAIXO ★ ---

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