from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from apply_for_a_licence.models import Document


def craft_apply_for_a_licence_url(path: str) -> str:
    """Crafts and returns a full, complete URL for a path in the apply_for_a_licence."""
    return f"{settings.PROTOCOL}{settings.APPLY_FOR_A_LICENCE_DOMAIN}{path}"


def get_file_s3_key(instance: "Document", filename: str) -> str:
    """Generate a unique S3 key for the file, with the licence ID as a prefix."""
    return f"{instance.licence.pk}/{filename}"
