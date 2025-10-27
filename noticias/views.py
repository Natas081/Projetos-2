from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

# REGISTRO
def registro_usuario(request):
    """
    Exibe o formulário de registro de novo usuário e salva no banco de dados.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada com sucesso para {username}!')
            login(request, user)  # opcional: loga o usuário automaticamente
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})


# LOGIN
def login_usuario(request):
    """
    Tela de login.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    return render(request, 'registration/login.html')


# LOGOUT
def logout_usuario(request):
    """
    Desloga o usuário.
    """
    logout(request)
    messages.info(request, 'Você saiu da conta.')
    return redirect('login')
