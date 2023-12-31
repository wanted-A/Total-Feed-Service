from pathlib import Path
import os
import environ
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.

# .env 설정
env = environ.Env(DEBUG=(bool, False))

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(env_file=os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",  # swagger
]

CUSTOM_APPS = [
    "users.apps.UsersConfig",
    "boards.apps.BoardsConfig",
    "common.apps.CommonConfig",
]

SYSTEM_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

INSTALLED_APPS = SYSTEM_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": env("DB_NAME"),
#         "USER": env("DB_USER"),
#         "PASSWORD": env("DB_PASSWORD"),
#         "HOST": env("DB_HOST"),
#         "PORT": env("DB_PORT"),
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

DATE_INPUT_FORMATS = ["%Y-%m-%d"]

DATETIME_FORMAT = "Y-m-d H:i:s"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# users 설정
AUTH_USER_MODEL = "users.User"

# REST_FRAMEWORK
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        # 전역 설정중 (IsAuthenticated 를 모든 views 에 적용)
        # 만약 불필요 할 경우, 해당 view class 에서 permission_classes 를 지정하면 됨
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "boards.pagination.CustomPageNumberPagination",
    "PAGE_SIZE": 10,
}


# simplejwt 설정
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=60),  # 리프레시 토큰 유효 시간
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Swagger 토큰 인증
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "DRF Token": {"type": "apiKey", "name": "Authorization", "in": "header"}
    }
}

## 이메일 인증 시작 ##
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"  # 메일을 보내는 방식
EMAIL_HOST = env("EMAIL_HOST")  # 메일을 호스트 하는 서버
EMAIL_PORT = 587  # 메일과 통신하는 포트
EMAIL_USE_TLS = True  # TLS 보안 사용
EMAIL_HOST_USER = env("EMAIL_HOST_USER")  # 발신할 네이버 이메일
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")  # 네이버 앱 비밀번호
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER  # 사이트와 관련한 자동 응답 받을 이메일 주소

ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # 이메일 인증을 필수로 설정
ACCOUNT_EMAIL_ON_GET = True  # 이메일 인증시 이메일을 보내줌
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[회원가입 이메일 인증] "  # 이메일에 자동으로 표시되는 제목
ACCOUNT_CONFIRM_EMAIL_ON_GET = True  # 유저가 받은 링크를 클릭하면 회원가입 완료

ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5  # 로그인 실패 횟수 제한