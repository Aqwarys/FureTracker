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




# # --- AWS S3 Storage Settings (always defined, but used conditionally) ---
# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'eu-central-1') # Specify your S3 region
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com' if AWS_STORAGE_BUCKET_NAME else None

# # Settings for signed URLs (if you use them for media access)
# # If your media files should be publicly accessible without signed URLs, set AWS_QUERYSTRING_AUTH = False
# AWS_QUERYSTRING_AUTH = True
# AWS_QUERYSTRING_EXPIRE = 3600 # URL validity in seconds (e.g., 1 hour)


# # --- Conditional Static and Media File Handling ---

# if DEBUG:
#     # --- LOCAL STATIC AND MEDIA SETTINGS FOR DEVELOPMENT ---

#     # URL for static files (served locally by Django's development server)
#     STATIC_URL = '/static/'
#     # The absolute path to the directory where `collectstatic` will gather static files during development
#     STATIC_ROOT = BASE_DIR / 'staticfiles_collected' # Ensure this path is correct

#     # Directories where Django looks for static files of your apps (in addition to app's 'static' folders)
#     STATICFILES_DIRS = [
#         BASE_DIR / 'static', # Your project-level static files (e.g., custom_admin.css)
#     ]

#     # URL for media files (served locally by Django's development server)
#     MEDIA_URL = '/media/'
#     # The absolute path to the directory where user-uploaded media files will be stored locally
#     MEDIA_ROOT = BASE_DIR / 'media'

#     # Use Django's default FileSystemStorage for both default (media) and staticfiles
#     STORAGES = {
#         "default": {
#             "BACKEND": "django.core.files.storage.FileSystemStorage",
#         },
#         "staticfiles": {
#             "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
#         },
#     }

# else:
#     # --- S3 STATIC AND MEDIA SETTINGS FOR PRODUCTION ---

#     # URL for media files (will be served from S3)
#     MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

#     # URL for static files (will be served from S3)
#     STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"

#     # Directories where Django looks for static files of your apps (during collectstatic)
#     STATICFILES_DIRS = [
#         BASE_DIR / "static", # Your project-level static files (e.g., custom_admin.css)
#     ]
#     # STATIC_ROOT - where `collectstatic` gathers static files BEFORE uploading to S3
#     STATIC_ROOT = BASE_DIR / "staticfiles_collected" # This path is still used by collectstatic

#     # STORAGES configuration for S3
#     STORAGES = {
#         "default": { # This storage is for your media files (including videos)
#             "BACKEND": "storages.backends.s3.S3Storage",
#             "OPTIONS": {
#                 "bucket_name": AWS_STORAGE_BUCKET_NAME,
#                 "region_name": AWS_S3_REGION_NAME,
#                 "querystring_auth": AWS_QUERYSTRING_AUTH,
#                 "querystring_expire": AWS_QUERYSTRING_EXPIRE,
#                 "custom_domain": AWS_S3_CUSTOM_DOMAIN, # Use the general custom domain
#                 "url_protocol": "https:", # Use HTTPS
#                 "location": "media", # <-- IMPORTANT: All media files will be in the 'media/' folder
#                 "object_parameters": {
#                     "ContentDisposition": "inline", # Crucial for in-browser playback
#                     "CacheControl": "max-age=86400", # Cache for 24 hours
#                     # "ContentType": "video/mp4", # Uncomment ONLY if ALL default uploads are MP4
#                 },
#             },
#         },
#         "staticfiles": { # This storage is for your static files
#             "BACKEND": "storages.backends.s3.S3Storage",
#             "OPTIONS": {
#                 "bucket_name": AWS_STORAGE_BUCKET_NAME,
#                 "region_name": AWS_S3_REGION_NAME,
#                 "querystring_auth": False, # Static files are usually public and don't require signed URLs
#                 "custom_domain": AWS_S3_CUSTOM_DOMAIN, # Use the general custom domain
#                 "url_protocol": "https:",
#                 "location": "static", # <-- IMPORTANT: All static files will be in the 'static/' folder
#                 "object_parameters": {
#                     "CacheControl": "max-age=86400",
#                 },
#             },
#         },
#     }












# --- STATIC AND MEDIA URLS ---
# URL для медиафайлов (будет обслуживаться с S3)
MEDIA_URL = f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/media/"


# URL для статических файлов (будет обслуживаться с S3)
STATIC_URL = f"https://{os.getenv('AWS_STORAGE_BUCKET_NAME')}.s3.{os.getenv('AWS_S3_REGION_NAME')}.amazonaws.com/static/"

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
    "site_icon": "favicon.ico", # Favicon для сайта

    # Приветствие
    "welcome_sign": "Добро пожаловать в панель управления!",

    # Копирайт в футере
    "copyright": "ТОО 'Ваша Компания' 2024",

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
    "show_ui_builder": True, # Установите в True для включения конструктора UI (для настройки темы)
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