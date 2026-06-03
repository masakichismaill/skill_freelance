"""
本番環境設定。
使用方法:
  DJANGO_SETTINGS_MODULE=skill_freelance.settings_production gunicorn skill_freelance.wsgi
"""
from .settings import *  # noqa: F401, F403

DEBUG = False

SECRET_KEY = env("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# WhiteNoise を SecurityMiddleware の直後に挿入
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# Static files
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# HTTPS 関連（リバースプロキシ使用時）
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
