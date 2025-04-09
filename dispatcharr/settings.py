import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'REPLACE_ME_WITH_A_REAL_SECRET'
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_DB = os.environ.get("REDIS_DB", "0")

# Set DEBUG to True for development, False for production
if os.environ.get('DISPATCHARR_DEBUG', 'False').lower() == 'true':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'apps.api',
    'apps.accounts',
    'apps.channels.apps.ChannelsConfig',
    'apps.dashboard',
    'apps.downloads',  # Add this line for the downloads app
    'apps.epg',
    'apps.hdhr',
    'apps.m3u',
    'apps.output',
    'apps.proxy.apps.ProxyConfig',
    'apps.proxy.ts_proxy',
    'core',
    'daphne',
    'drf_yasg',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django_filters',
    'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'core.middleware.CustomCsrfMiddleware',  # Add our custom middleware
]


ROOT_URLCONF = 'dispatcharr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'frontend/dist'),
            BASE_DIR / "templates"
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = 'dispatcharr.wsgi.application'
ASGI_APPLICATION = 'dispatcharr.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, 6379, REDIS_DB)],  # Ensure Redis is running
        },
    },
}

if os.getenv('DB_ENGINE', None) == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/data/dispatcharr.db',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'dispatcharr'),
            'USER': os.environ.get('POSTGRES_USER', 'dispatch'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'secret'),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': int(os.environ.get('POSTGRES_PORT', 5432)),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
      'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
      }
   }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'  # Directory where static files will be collected

# Adjust STATICFILES_DIRS to include the paths to the directories that contain your static files.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'frontend/dist'),  # React build static files
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Configure Redis key prefix
CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = {
    'global_keyprefix': 'celery-tasks:',  # Set the Redis key prefix for Celery
}

# Set TTL (Time-to-Live) for task results (in seconds)
CELERY_RESULT_EXPIRES = 3600  # 1 hour TTL for task results

# Optionally, set visibility timeout for task retries (if using Redis)
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': 3600,  # Time in seconds that a task remains invisible during retries
}

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
    'fetch-channel-statuses': {
        'task': 'core.tasks.beat_periodic_task',
        'schedule': 2.0,
    },
}

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'


SERVER_IP = "127.0.0.1"

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    'http://*',
    'https://*',
    'http://10.0.0.10:9192',  # Add your specific origin
]
APPEND_SLASH = True

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,  # Optional: Whether to rotate refresh tokens
    'BLACKLIST_AFTER_ROTATION': True,  # Optional: Whether to blacklist refresh tokens
}

# Redis connection settings
REDIS_URL = 'redis://localhost:6379/0'
REDIS_SOCKET_TIMEOUT = 60  # Socket timeout in seconds
REDIS_SOCKET_CONNECT_TIMEOUT = 5  # Connection timeout in seconds
REDIS_HEALTH_CHECK_INTERVAL = 15  # Health check every 15 seconds
REDIS_SOCKET_KEEPALIVE = True  # Enable socket keepalive
REDIS_RETRY_ON_TIMEOUT = True  # Retry on timeout
REDIS_MAX_RETRIES = 10  # Maximum number of retries
REDIS_RETRY_INTERVAL = 1  # Initial retry interval in seconds

# Proxy Settings
PROXY_SETTINGS = {
    'HLS': {
        'DEFAULT_URL': '',  # Default HLS stream URL if needed
        'BUFFER_SIZE': 1000,
        'USER_AGENT': 'VLC/3.0.20 LibVLC/3.0.20',
        'CHUNK_SIZE': 8192,
        'CLIENT_POLL_INTERVAL': 0.1,
        'MAX_RETRIES': 3,
        'MIN_SEGMENTS': 12,
        'MAX_SEGMENTS': 16,
        'WINDOW_SIZE': 12,
        'INITIAL_SEGMENTS': 3,
    },
    'TS': {
        'DEFAULT_URL': '',  # Default TS stream URL if needed
        'BUFFER_SIZE': 1000,
        'RECONNECT_DELAY': 5,
        'USER_AGENT': 'VLC/3.0.20 LibVLC/3.0.20',
        'REDIS_CHUNK_TTL': 60,  # How long to keep chunks in Redis (seconds)
    }
}
