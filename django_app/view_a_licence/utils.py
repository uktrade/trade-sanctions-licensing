from django.conf import settings


def craft_view_a_licence_url(path: str) -> str:
    """Crafts and returns a full, complete URL for a path in the view_a_licence_app."""
    return f"{settings.PROTOCOL}{settings.VIEW_A_LICENCE_DOMAIN}{path}"
