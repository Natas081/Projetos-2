# cria_admin.py

from django.contrib.auth.models import User
from noticias.models import Categoria # Importe seu modelo de Categoria

# --- CREDENCIAIS E DADOS INICIAIS ---
USERNAME = "felipe"
EMAIL = "felipe@gmail.com"
PASSWORD = "nautico" 
CATEGORIAS_INICIAIS = ['Tecnologia', 'Esportes', 'Política', 'Economia', 'Medicina', 'Carros', 'Cinema', 'Ciência', 'Games', 'Meio ambiente']

def run_script():
    # 1. Cria o Superusuário (Se não existir)
    if not User.objects.filter(username=USERNAME).exists():
        User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
        print(f"Superusuário '{USERNAME}' criado.")

    # 2. Cria as Categorias (Se não existirem)
    for nome_categoria in CATEGORIAS_INICIAIS:
        if not Categoria.objects.filter(nome=nome_categoria).exists():
            Categoria.objects.create(nome=nome_categoria)
            print(f'Categoria "{nome_categoria}" criada.')