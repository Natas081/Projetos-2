"""
Django settings for project project.
"""

from pathlib import Path
import os
import dj_database_url

# -------------------- DIRETÓRIO BASE --------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------- CHAVE SECRETA --------------------
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-41sq)-djgpt%*ggw(c!a4+f7kfenhv90uyp3-f2tdvdgqrz=m!'
)

# -------------------- DEBUG --------------------
DEBUG = os.environ.get('DEBUG', '') == '1'


# -------------------- HOSTS PERMITIDOS --------------------
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.onrender.com',       # ✅ Permite seu domínio do Render
]

# -------------------- APLICAÇÕES INSTALADAS --------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # App principal
    'noticias',

    # Suporte a arquivos estáticos no Render
    'whitenoise.runserver_nostatic',
]

# -------------------- MIDDLEWARE --------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ WhiteNoise deve ficar logo abaixo de Security
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -------------------- URLS E TEMPLATES --------------------
ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [BASE_DIR / 'templates'],  # ✅ Diretório global de templates

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # ✅ Context processor do streak
                'noticias.context_processors.streak_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# -------------------- BANCO DE DADOS --------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ✅ Usar banco do Render, caso exista
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )

# -------------------- VALIDAÇÃO DE SENHA --------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------- IDIOMA E FUSO HORÁRIO --------------------
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# -------------------- ARQUIVOS ESTÁTICOS --------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# -------------------- ARQUIVOS DE MÍDIA (uploads) --------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -------------------- CONFIGURAÇÕES DE LOGIN --------------------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# -------------------- CHAVE PADRÃO DE PK --------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
