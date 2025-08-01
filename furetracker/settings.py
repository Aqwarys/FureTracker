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
    'jazzmin',
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
import dj_database_url

DATABASE_URL = os.getenv('DATABASE_URL')


if not DATABASE_URL:
    raise ImproperlyConfigured("DATABASE_URL is not set in the environment. It is required for all environments.")

DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
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

# -------------------
# LOGGING
# -------------------

LOGGING = {
    'version': 1, # Версия схемы логирования. Всегда 1.
    'disable_existing_loggers': False, # Не отключать существующие логгеры (например, Django's по умолчанию)

    # 1. Форматтеры: Как будут выглядеть ваши сообщения в логах
    'formatters': {
        'verbose': { # Для детальных логов (продакшен)
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': { # Для простых логов (локальная разработка)
            'format': '{levelname} {message}',
            'style': '{',
        },
    },

    # 2. Фильтры: Дополнительная фильтрация сообщений
    'filters': {
        'require_debug_true': { # Сообщения только при DEBUG=True
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': { # Сообщения только при DEBUG=False
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },

    # 3. Хендлеры: Куда отправлять логи
    'handlers': {
        'console': { # Вывод логов в консоль (stdout/stderr)
            'level': 'INFO', # Минимальный уровень для вывода в консоль
            'filters': ['require_debug_true'], # Только при DEBUG=True
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': { # Вывод логов в файл (для продакшена)
            'level': 'INFO', # Минимальный уровень для записи в файл
            'filters': ['require_debug_false'], # Только при DEBUG=False
            'class': 'logging.handlers.RotatingFileHandler', # Ротация файла, чтобы не рос бесконечно
            'filename': '/var/log/django/furetracker.log', # Путь к файлу логов на сервере
            'maxBytes': 1024 * 1024 * 5, # 5 MB на файл
            'backupCount': 5, # Хранить 5 старых файлов логов
            'formatter': 'verbose',
        },
        'mail_admins': { # Отправка ERROR/CRITICAL логов администраторам по почте
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
             # Обязательно настроить EMAIL_BACKEND, EMAIL_HOST и ADMINS
        },
    },

    # 4. Логгеры: Кто генерирует логи и какие хендлеры их обрабатывают
    'loggers': {
        'django': { # Логгер для Django-сообщений (SQL-запросы, ошибки и т.д.)
            'handlers': ['console', 'file'], # Отправлять и в консоль, и в файл
            'level': 'INFO', # Начинаем с INFO, можно поднять до DEBUG для детальной отладки
            'propagate': False, # Не передавать логи выше по иерархии (чтобы не дублировались)
        },
        'django.request': { # Логгер для HTTP-запросов и ошибок (4xx/5xx)
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'ERROR', # Отправляем ошибки запросов администраторам
            'propagate': False,
        },
        'orders': { # Логгер для вашего приложения 'orders'
            'handlers': ['console', 'file'],
            'level': 'INFO', # Уровень для вашего приложения
            'propagate': False,
        },
        # Добавьте логгеры для других ваших приложений ('consultations', 'main', 'core')
        'consultations': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'main': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },

    # 5. Root Logger: Логгер по умолчанию, если сообщение не обрабатывается специфичным логгером
    'root': {
        'handlers': ['console', 'file'],
        'level': 'WARNING', # По умолчанию все остальные сообщения выше WARNING
    }
}


# --- STATIC AND MEDIA URLS ---

# STATICFILES_DIRS - это папки, где Django ищет статику ваших приложений
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

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
                "CacheControl": "max-age=86400",

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


# DEFAULT STORAGE CHECKER
# from django.core.files.storage import default_storage
# print(default_storage.__class__)

# settings.py
JAZZMIN_SETTINGS = {
    # Общие настройки сайта
    "site_header": "Панель Бизнеса", # Шапка админки
    "site_brand": "Управление Заказами", # Заголовок бренда
    "site_logo": "images/logo.png",  # Путь к вашему логотипу в папке STATICFILES_DIRS/static (например, 'static/img/logo.png')
    "login_logo_dark": None, # Можно использовать темный логотип для темной темы логина
    "site_icon": "images/logo.png", # Favicon для сайта

    # Приветствие
    "welcome_sign": "Добро пожаловать в панель управления!",

    # Копирайт в футере
    "copyright": "BaizhigitMebel 2025",

    # Дополнительные ссылки в верхнем меню (например, ссылка на сайт)
    "topmenu_links": [
        {"name": "Главная",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Поддержка", "url": "https://github.com/farridav/django-jazzmin/issues", "new_window": True },
        # {"model": "auth.User"}, # Ссылка на пользователей
        # {"app": "orders"}, # Ссылка на приложение заказов
    ],

    # Отображение боковой панели
    "show_sidebar": True,
    "navigation_expanded": True, # Разворачивать навигацию по умолчанию

    # Фиксированная навигация
    "navbar_fixed": True,
    "sidebar_fixed": True,

    # Порядок отображения приложений
    "order_with_respect_to": ["orders", "consultation", "core.orderstatus", "auth"], # Свои приложения выше

    # Возможность переключать темную/светлую тему
    "show_ui_builder": DEBUG, # Установите в True для включения конструктора UI (для настройки темы)
                              # и НЕ ЗАБУДЬТЕ УСТАНОВИТЬ В FALSE В ПРОДАКШЕНЕ

    # Дополнительный CSS для Jazzmin
    "custom_css": "admin/css/custom_jazzmin.css", # Путь к вашему CSS в STATICFILES_DIRS/admin/css/
    # Дополнительный JS для Jazzmin
    # "custom_js": None,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-warning",
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-outline-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "actions_sticky_top": False
}