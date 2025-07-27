import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# -------------------
# BASE SETTINGS
# -------------------
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY is not set.")

DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')

# -------------------
# APPLICATIONS
# -------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd-party apps
    'django_filters',
    'storages',

    # Local apps
    'main',
    'core.apps.CoreConfig',
    'orders.apps.OrdersConfig',
    'consultations.apps.ConsultationsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'furetracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'furetracker.wsgi.application'

# -------------------
# DATABASE
# -------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -------------------
# PASSWORDS
# -------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------
# LANGUAGE & TIMEZONE
# -------------------
LANGUAGE_CODE = 'Ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True



# --- STATIC AND MEDIA URLS ---
# URL для медиафайлов (будет обслуживаться с S3)
MEDIA_URL = f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/media/"
# Если используете CloudFront или custom_domain:
# MEDIA_URL = f"https://{os.getenv('AWS_S3_CUSTOM_DOMAIN')}/media/"

# URL для статических файлов (будет обслуживаться с S3)
STATIC_URL = f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/static/"
# Если используете CloudFront или custom_domain, и AWS_S3_CUSTOM_DOMAIN определен:
# STATIC_URL = f"https://{os.getenv('AWS_S3_CUSTOM_DOMAIN')}/static/" # Убедитесь, что эта переменная окружения установлена!

# STATICFILES_DIRS - это папки, где Django ищет статику ваших приложений
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
# STATIC_ROOT - куда `collectstatic` собирает статику ПЕРЕД загрузкой на S3
STATIC_ROOT = BASE_DIR / "staticfiles_collected"
# AWS S3 Storage Settings
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'eu-central-1') # Укажите ваш регион S3
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com' if AWS_STORAGE_BUCKET_NAME else None

# Настройки для подписанных URL (если вы их используете для доступа к медиа)
# Если ваши медиафайлы должны быть публично доступны без подписанных URL, установите AWS_QUERYSTRING_AUTH = False
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600 # Срок действия URL в секундах (например, 1 час)

STORAGES = {
    "default": { # Это хранилище для ваших медиафайлов (включая видео)
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
            "querystring_auth": AWS_QUERYSTRING_AUTH,
            "querystring_expire": AWS_QUERYSTRING_EXPIRE,
            "custom_domain": AWS_S3_CUSTOM_DOMAIN, # Используем общий кастомный домен
            "url_protocol": "https:", # Использовать HTTPS
            "location": "media", # <-- ЭТО ОЧЕНЬ ВАЖНО: Все медиафайлы будут в папке media/
            "object_parameters": {
                # --- ЭТИ ПАРАМЕТРЫ КЛЮЧЕВЫЕ ДЛЯ ВОСПРОИЗВЕДЕНИЯ В БРАУЗЕРЕ ---
                # 1. Content-Disposition: 'inline' говорит браузеру отображать файл, а не скачивать его.
                "ContentDisposition": "inline",
                # 2. Cache-Control: Настройки кэширования для браузера. Устанавливает, как долго браузер
                #    может кэшировать файл. 86400 секунд = 24 часа.
                "CacheControl": "max-age=86400",
                # Content-Type: Django-storages обычно хорошо определяет его автоматически.
                # Если он не справляется, и у вас *только* видео в этом хранилище, можно явно указать:
                # "ContentType": "video/mp4", # Раскомментируйте ТОЛЬКО если все default-загрузки это MP4
            },
        },
    },
    "staticfiles": { # Это хранилище для ваших статических файлов
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "region_name": AWS_S3_REGION_NAME,
            "querystring_auth": False, # Статические файлы обычно публичны и не требуют подписанных URL
            "custom_domain": AWS_S3_CUSTOM_DOMAIN, # Используем общий кастомный домен
            "url_protocol": "https:",
            "location": "static", # <-- ЭТО ОЧЕНЬ ВАЖНО: Все статические файлы будут в папке static/
            "object_parameters": {
                "CacheControl": "max-age=86400",
            },
        },
    },
}

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/' if AWS_S3_CUSTOM_DOMAIN else '/media/'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/' if AWS_S3_CUSTOM_DOMAIN else '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

from django.core.files.storage import default_storage
print(default_storage.__class__)