from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def registro_usuario(request):
    """
    Exibe o formulário de registro de novo usuário e salva no banco de dados.
    Usa o UserCreationForm padrão do Django.
    """

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada com sucesso para {username}!')
            return redirect('login')  # volta pra tela de login após cadastro
    else:
        form = UserCreationForm()

    # Corrigido: template certo dentro da pasta registration
    return render(request, 'registration/registro.html', {'form': form})
