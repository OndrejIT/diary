import os
import sys
import socket

import yaml
from easydict import EasyDict

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load config file
CONFIGFILE = os.environ.get("CONFIGFILE")
CONFIG = EasyDict(yaml.load(open(CONFIGFILE, "r"), Loader=yaml.FullLoader))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG.secret

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = CONFIG.debug

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "raven.contrib.django.raven_compat",
    "axes",
    "reversion",
    "modules.user",
    "modules.diary",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "resources/templates/")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": CONFIG.database.name,
        "USER": CONFIG.database.user,
        "PASSWORD": CONFIG.database.password,
        "HOST": CONFIG.database.host,
        "PORT": CONFIG.database.port,
        "CONN_MAX_AGE": CONFIG.database.age,
    }
}

AUTH_USER_MODEL = "user.User"

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Logging
DEFAULT_LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
DEFAULT_LOG_HANDLERS = ["console", "sentry"]

# FIXME vyresit lepe? V shellu nechceme sentry a podrobne logovani.
try:
    if "shell" in sys.argv[1]:
        DEFAULT_LOG_LEVEL = "ERROR"
        DEFAULT_LOG_HANDLERS = ["console"]
        CONFIG.sentry_dsn = None
except IndexError:
    pass

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {
        "level": DEFAULT_LOG_LEVEL,
        "handlers": DEFAULT_LOG_HANDLERS,
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "formatters": {
        "simple": {
            "format": "%(levelname)-8s [%(name)s:%(lineno)s] %(message)s",
        },
        "standard": {
            "format": "%(asctime)s %(levelname)-8s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": DEFAULT_LOG_LEVEL,
            "formatter": "standard" if DEBUG else "simple",
        },
        "sentry": {
            "class": "raven.contrib.django.raven_compat.handlers.SentryHandler",
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "tags": {
                "fqdn": socket.getfqdn(),
            },
        },
    },
    "loggers": {
        "django": {
            "level": "INFO",
            "handlers": DEFAULT_LOG_HANDLERS,
            "propagate": False,
        },
        "raven": {
            "level": DEFAULT_LOG_LEVEL,
            "handlers": ["console"],
            "propagate": False,
        },
        "sentry.errors": {
            "level": DEFAULT_LOG_LEVEL,
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

RAVEN_CONFIG = {
    "dsn": CONFIG.sentry_dsn if not DEBUG else None,
}

RADICALE_CONFIG = {
    "server": {
        "realm": "Diary - Password Required",
    },
    "encoding": {
        "request": "utf-8",
        "stock": "utf-8",
    },
    "auth": {
        "type": "modules.diary.auth",
    },
    "web": {
        "type": "radicale_infcloud",
    },
    # FIXME pak udelat jinak
#    "rights": {
#        "type":  "modules.diary.rights",
#    },
    "storage": {
        "type": "modules.diary.storage",
        "filesystem_folder": "/srv",
    }
#    "storage": {
#         "filesystem_folder": "/srv"
#    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "axes_cache": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

RADICALE_RIGHTS = {
    "rw": {
        "user": ".+",
        "collection": "^%(login)s/[a-z0-9\.\-_]+\.(vcf|ics)$",
        "permission": "rw",
    },
    "rw-root": {
        "user": ".+",
        "collection": "^%(login)s$",
        "permission": "rw",
    },
}

AXES_CACHE = "axes_cache"
AXES_META_PRECEDENCE_ORDER = ["HTTP_X_FORWARDED_FOR", "HTTP_X_REAL_IP"]
AXES_LOCKOUT_TEMPLATE = "/account/lockout.jinja"
AXES_FAILURE_LIMIT = CONFIG.axes.failure_limit
AXES_COOLOFF_TIME = CONFIG.axes.cooloff_time

STATIC_URL = CONFIG.static_url
STATIC_ROOT = os.path.join(BASE_DIR, "resources/static")

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = "cs"

TIME_ZONE = "Europe/Prague"

USE_I18N = True

USE_L10N = True

USE_TZ = True
