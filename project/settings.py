"""
Django settings for project project.
...
"""

from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# -------------------- CORREÇÃO DA SECRET KEY --------------------
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-41sq)-djgpt%*ggw(c!a4+f7kfenhv90uyp3-f2tdvdgqrz=m!')
# -----------------------------------------------------------------


# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG MODIFICADO (desliga automaticamente no Render)
DEBUG = 'RENDER' not in os.environ

# -------------------- CORREÇÃO CRÍTICA DO ALLOWED_HOSTS --------------------
# Garante que hosts de produção sejam aceitos. 
# Adiciona o host do Render E o subdomínio genérico para evitar problemas.
ALLOWED_HOSTS = ['127.0.0.1', 'localhost'] # Hosts locais

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    # Adiciona o subdomínio genérico do Render para maior compatibilidade
    ALLOWED_HOSTS.append('.onrender.com')
# ---------------------------------------------------------------------------


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'noticias',
    # Adicione aqui o Whitenoise se você usar um Django mais recente:
    # 'whitenoise.runserver_nostatic', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # --- ADIÇÃO NECESSÁRIA PARA O CSS NO RENDER (MUITO BEM!) ---
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # --------------------------------------------
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True
    )


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/' # <-- CORREÇÃO: ADICIONADO STATIC_URL

STATICFILES_DIRS = [ 
    os.path.join(BASE_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# --- CONFIGURAÇÃO DO WHITE NOISE (CSS/JS) ---
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# ---------------------------------------------


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------- ADIÇÃO NECESSÁRIA PARA REDIRECIONAMENTO --------------------
# Garante que o Django saiba para onde ir após o login/logout.
LOGIN_URL = '/accounts/login/' # URL padrão do Django Auth
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
# ----------------------------------------------------------------------------------