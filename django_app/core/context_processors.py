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


def back_button(request: HttpRequest) -> dict[str, str]:
    """Default back button values - can be overridden in the context dictionary of a view."""
    return {"back_button_text": "Back", "back_button_link": request.META.get("HTTP_REFERER", None)}


def session_expiry_times(request: HttpRequest) -> dict[str, int]:
    """Add the session expiry time in seconds & minutes to the context."""
    return {
        "session_expiry_seconds": settings.SESSION_COOKIE_AGE,
        "session_expiry_minutes": settings.SESSION_COOKIE_AGE // 60,
        "session_expiry_hours": settings.SESSION_COOKIE_AGE // 60 // 60,
    }
