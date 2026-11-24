from urllib.parse import urlparse

from django.core.exceptions import ValidationError

ALLOWED_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"}


def validate_youtube_url(value):
    if not value:
        return
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https"):
        raise ValidationError("Ссылка должна начинаться с http:// или https://")
    if parsed.netloc.lower() not in ALLOWED_HOSTS:
        raise ValidationError("Разрешены только ссылки на youtube.com")
