from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from datetime import date, timedelta
from .models import Interest, Noticia, Perfil, CheckIn, Goal, DiarioEntry
from .models import UserProfile
from .forms import UsernameChangeForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# -----------------------------
# PÁGINAS PRINCIPAIS
# -----------------------------
def home(request):
    noticias = Noticia.objects.all().order_by('-id')[:5]
    perfil = getattr(request.user, 'perfil', None)
    return render(request, 'noticias/home.html', {"noticias": noticias, "perfil": perfil})

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
# RESUMO SEMANAL
# -----------------------------
@login_required
def resumo_semanal_view(request):
    perfil = getattr(request.user, 'perfil', None)
    hoje = timezone.localdate()

    primeiro_checkin = CheckIn.objects.filter(usuario=request.user).order_by('data_checkin').first()
    
    # Se o usuário NUNCA fez check-in, ele é novo e sem atividades.
    # Mostra a mensagem de "boas-vindas" do Cenário 3.
    if not primeiro_checkin:
        mensagem = "Seu resumo semanal aparecerá aqui! Comece a adicionar anotações para ver seu progresso."
        return render(request, 'noticias/resumo_semanal.html', {"mensagem": mensagem, "perfil": perfil})

    # Se chegou aqui, o usuário tem pelo menos 1 check-in.
    # Vamos buscar as atividades da semana.
    semana_inicio = hoje - timedelta(days=hoje.weekday())
    semana_fim = semana_inicio + timedelta(days=6)

    interesses_novos = Interest.objects.filter(
        user=request.user, 
        goals__weekStartDate=semana_inicio
    ).distinct()

    maior_interesse = Goal.objects.filter(
        user=request.user, 
        weekStartDate=semana_inicio
    ).order_by('-currentProgress').first()

    anotacoes_semana = DiarioEntry.objects.filter(
        usuario=request.user,
        data_criacao__date__range=(semana_inicio, semana_fim)
    )

    # Verifica se as 3 buscas não trouxeram resultados
    if not interesses_novos.exists() and not maior_interesse and not anotacoes_semana.exists():
        
        # OK, está vazio. Mas por quê?
        # Calculamos os dias de uso para decidir qual mensagem mostrar.
        dias_de_uso = (hoje - primeiro_checkin.data_checkin).days
        
        if dias_de_uso < 7:
            # Cenário 3 (Novo): Usuário novo, mas sem atividades *esta semana*
            mensagem = "Seu resumo semanal aparecerá aqui! Comece a adicionar anotações para ver seu progresso."
        else:
            # Cenário 2: Usuário antigo, mas sem atividades *esta semana*
            mensagem = "Nenhuma novidade nesta semana."
        
        return render(request, 'noticias/resumo_semanal.html', {"mensagem": mensagem, "perfil": perfil})

    # Cenário 1: O usuário tem atividades! Mostra o resumo completo.
    return render(request, 'noticias/resumo_semanal.html', {
        "interesses_novos": interesses_novos,
        "maior_interesse": maior_interesse,
        "anotacoes_semana": anotacoes_semana,
        "perfil": perfil
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


# -----------------------------
# PROFILE UPDATE
# -----------------------------

@login_required
def settings_view(request):
    # Garante que o perfil exista (evita DoesNotExist -> 500)
    perfil, _ = UserProfile.objects.get_or_create(user=request.user)

    # Inicializa forms "não bindados" por padrão
    pform = ProfileForm(instance=perfil)
    uform = UsernameChangeForm(request.user)

    if request.method == "POST":
        # Salvar PERFIL (display_name + avatar)
        if "save_profile" in request.POST:
            pform = ProfileForm(request.POST, request.FILES, instance=perfil)
            if pform.is_valid():
                pform.save()
                messages.success(request, "Perfil atualizado com sucesso!")
                return redirect("settings")

        # Salvar USERNAME (trocar usuário de login)
        elif "save_username" in request.POST:
            uform = UsernameChangeForm(request.user, request.POST)
            if uform.is_valid():
                uform.save()
                messages.success(request, "Usuário alterado com sucesso!")
                return redirect("settings")

        # Outros POSTs caem aqui e só re-renderizam com os forms atuais

    # Monta avatar_url com segurança (evita .url sem arquivo)
    avatar_url = None
    try:
        if getattr(perfil, "avatar", None) and getattr(perfil.avatar, "name", ""):
            avatar_url = perfil.avatar.url
    except Exception:
        avatar_url = None

    # Fallback do nome de exibição
    display_name = (perfil.display_name or request.user.get_username()).strip()

    context = {
        "pform": pform,
        "uform": uform,
        "avatar_url": avatar_url,
        "display_name": display_name,
    }
    return render(request, "noticias/settings.html", context)


# -----------------------------
# INTERESSES
# -----------------------------
# No seu arquivo views.py

@login_required 
def gerenciar_interesses(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Você precisa estar logado para gerenciar interesses.')
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('name')
        target_frequency = request.POST.get('target_frequency')

        if name:
            # 1. Busca ou cria o Interesse
            interest, interest_created = Interest.objects.get_or_create(user=request.user, name=name)
            
            if interest_created:
                messages.success(request, f'Interesse "{name}" adicionado!')
            # (Opcional: adicione um else para dizer "Interesse já existe")

            # 2. Verifica se uma meta foi definida
            if target_frequency and target_frequency.isdigit():
                week_start = Goal.get_start_of_week()
                
                # --- AQUI ESTÁ A CORREÇÃO ---
                # Em vez de .create(), usamos .update_or_create()
                goal, goal_created = Goal.objects.update_or_create(
                    # Campos para BUSCAR:
                    user=request.user,
                    interest=interest,
                    weekStartDate=week_start,
                    
                    # Campos para ATUALIZAR ou CRIAR:
                    defaults={
                        'targetFrequency': int(target_frequency)
                        # Nota: Se a meta for nova, 'currentProgress' 
                        # usará o valor default (0). Se for atualização,
                        # o progresso atual será mantido.
                    }
                )
                # --- FIM DA CORREÇÃO ---

                if goal_created:
                    messages.success(request, f'Meta semanal criada: {target_frequency} leituras.')
                else:
                    messages.success(request, f'Meta semanal atualizada para: {target_frequency} leituras.')

            return redirect('pagina_de_interesses')

    interests_list = Interest.objects.filter(user=request.user)
    return render(request, 'noticias/interesses.html', {"interests": interests_list})

@login_required
def delete_interest_view(request, interest_id):
    interest = get_object_or_404(Interest, id=interest_id, user=request.user)
    if request.method == 'POST':
        interest.delete()
        messages.success(request, "Interesse deletado com sucesso!")
    return redirect('routine')

# (Cole isso no seu views.py)

@login_required
def edit_interest_view(request, interest_id):
    # 1. Busca o interesse específico daquele usuário
    interest = get_object_or_404(Interest, id=interest_id, user=request.user)
    
    # 2. Busca a meta DESTA semana (pode ser None)
    week_start = Goal.get_start_of_week()
    goal = Goal.objects.filter(
        user=request.user, 
        interest=interest, 
        weekStartDate=week_start
    ).first()

    if request.method == 'POST':
        # 3. Pega os dados do formulário
        new_name = request.POST.get('name')
        new_target_frequency_str = request.POST.get('target_frequency')

        # 4. Valida o nome
        if not new_name or new_name.strip() == "":
            messages.error(request, "O nome do interesse não pode ficar em branco.")
            # Se der erro, re-renderiza a página com os dados atuais
            return render(request, 'noticias/edit_interest.html', {
                'interest': interest,
                'goal': goal
            })
        
        # Salva o novo nome do interesse
        interest.name = new_name.strip()
        interest.save()

        # 5. Valida e salva a Meta
        try:
            # Converte a frequência (se for vazia, vira 0)
            new_target_frequency = int(new_target_frequency_str) if new_target_frequency_str else 0
        except ValueError:
            messages.error(request, "A frequência deve ser um número.")
            return render(request, 'noticias/edit_interest.html', {
                'interest': interest,
                'goal': goal
            })

        if new_target_frequency > 0:
            # Se o usuário quer uma meta (criar ou atualizar)
            if goal:
                # Meta já existe? Atualiza
                goal.targetFrequency = new_target_frequency
                goal.save()
                messages.success(request, f'Interesse "{interest.name}" e meta atualizados.')
            else:
                # Meta não existe? Cria
                Goal.objects.create(
                    user=request.user,
                    interest=interest,
                    targetFrequency=new_target_frequency,
                    currentProgress=0,
                    weekStartDate=week_start
                )
                messages.success(request, f'Interesse "{interest.name}" atualizado e meta criada.')
        
        elif new_target_frequency <= 0 and goal:
            # Se a meta é 0 e ela existia, delete
            goal.delete()
            messages.info(request, f'Interesse "{interest.name}" atualizado e meta da semana removida.')
        
        else:
            # Se a meta é 0 e não existia, só confirma a mudança do nome
            messages.success(request, f'Interesse "{interest.name}" atualizado.')

        # 6. Redireciona de volta para a Rotina
        return redirect('routine')

    # 7. (GET) Mostra a página de edição pela primeira vez
    context = {
        'interest': interest,
        'goal': goal # Passa a meta (ou None) para preencher o form
    }
    return render(request, 'noticias/edit_interest.html', context)

@login_required
def streak_page(request):
    perfil = getattr(request.user, 'perfil', None)
    today = date.today()

    if request.method == "POST":
        if not CheckIn.objects.filter(usuario=request.user, data_checkin=today).exists():
            # cria o check-in
            CheckIn.objects.create(usuario=request.user, data_checkin=today)

            # atualiza streak
            if perfil.ultimo_checkin == today - timedelta(days=1):
                # dia anterior foi check-in → incrementa streak
                perfil.leitura_streak += 1
            elif perfil.ultimo_checkin == today:
                # já fez check-in hoje, não muda
                messages.info(request, "Você já confirmou seu check-in hoje.")
                return redirect('streak')
            else:
                # não acessou ontem → streak reseta
                perfil.leitura_streak = 1

            perfil.ultimo_checkin = today
            perfil.save()

            messages.success(request, f"Check-in diário confirmado! Seu streak é {perfil.leitura_streak} dias.")
        else:
            messages.info(request, "Você já confirmou seu check-in hoje.")
        return redirect('streak')

    # GET: apenas exibe
    ja_fez_checkin_hoje = perfil.ultimo_checkin == today

    return render(request, 'noticias/streak.html', {
        'streak': perfil.leitura_streak,
        'perfil': perfil,
        'ja_fez_checkin_hoje': ja_fez_checkin_hoje,
    })
