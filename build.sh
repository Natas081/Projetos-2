#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. O comando que já estava lá (instalar dependências)
pip install -r requirements.txt

# 2. O comando que já estava lá (rodar migrações)
python manage.py collectstatic --no-input
python manage.py migrate

# 3. O NOVO comando (criar/atualizar o seu admin)
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()

username = '${DJANGO_SUPERUSER_USERNAME}'
email = '${DJANGO_SUPERUSER_EMAIL}'
password = '${DJANGO_SUPERUSER_PASSWORD}'

if User.objects.filter(username=username).exists():
    print('Superutilizador encontrado. ATUALIZANDO senha...')
    u = User.objects.get(username=username)
    u.set_password(password)
    u.save()
    print('Senha atualizada com sucesso!')
else:
    print('Superutilizador não encontrado. CRIANDO novo...')
    User.objects.create_superuser(username, email, password)
    print('Superutilizador criado com sucesso!')
"