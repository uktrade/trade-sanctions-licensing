from django.http import HttpRequest

from . import is_apply_for_a_licence_site, is_view_a_licence_site


def sites(request: HttpRequest) -> dict[str, bool]:
    if hasattr(request, "site"):
        return {
            "is_apply_for_a_licence_site": is_apply_for_a_licence_site(request.site),
            "is_view_a_licence_site": is_view_a_licence_site(request.site),
        }
    else:
        return {}
