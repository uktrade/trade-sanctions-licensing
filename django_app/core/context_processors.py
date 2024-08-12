from django.conf import settings
from django.http import HttpRequest


def truncate_words_limit(request: HttpRequest) -> dict[str, int]:
    return {
        "truncate_words_limit": settings.TRUNCATE_WORDS_LIMIT,
    }


def is_debug_mode(request: HttpRequest) -> dict[str, bool]:
    return {
        "is_debug_mode": settings.DEBUG,
    }
