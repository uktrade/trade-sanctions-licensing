from typing import TYPE_CHECKING

from apply_for_a_licence.choices import StatusChoices
from django.conf import settings

if TYPE_CHECKING:
    from apply_for_a_licence.models import Document, Licence
    from django.contrib.auth.models import User


def craft_apply_for_a_licence_url(path: str) -> str:
    """Crafts and returns a full, complete URL for a path in the apply_for_a_licence."""
    return f"{settings.PROTOCOL}{settings.APPLY_FOR_A_LICENCE_DOMAIN}{path}"


def get_active_regimes() -> list[dict[str, str]]:
    """Get the active sanctions regimes. If submodule is not present, return an empty list."""
    try:
        from sanctions_regimes.licensing import active_regimes
    except ImportError:
        active_regimes = []

    return active_regimes


def get_file_s3_key(instance: "Document", filename: str) -> str:
    """Generate a unique S3 key for the file, with the licence ID as a prefix."""
    return f"{instance.licence.pk}/{filename}"


def can_user_view_licence(user: "User", licence: "Licence") -> bool:
    """Check if the user can view the licence application."""
    return user == licence.user


def can_user_edit_licence(user: "User", licence: "Licence") -> bool:
    """Check if the user can edit the licence application."""
    return can_user_view_licence(user, licence) and licence.status == StatusChoices.draft
