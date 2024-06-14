import functools
from typing import Any

from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse


class SiteName:
    apply_for_a_licence = "apply-for-a-licence"
    view_a_licence = "view-a-licence"


def require_apply_for_a_licence() -> Any:
    def decorator(f: Any) -> Any:
        """Decorator to require that a view only accepts requests from the apply-for-a-licence site."""

        @functools.wraps(f)
        def _wrapped_view(request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
            if not is_apply_for_a_licence_site(request.site):
                raise PermissionDenied("View a breach feature requires view a breach site.")

            return f(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def require_view_a_licence() -> Any:
    def decorator(func: Any) -> Any:
        """Decorator to require that a view only accepts requests from the view-a-licence site."""

        @functools.wraps(func)
        def _wrapped_view(request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
            if not is_view_a_licence_site(request.site):
                raise PermissionDenied("Report a breach feature requires report a breach site.")
            return func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def is_apply_for_a_licence_site(site: Site) -> bool:
    return site.name == SiteName.apply_for_a_licence


def is_view_a_licence_site(site: Site) -> bool:
    return site.name == SiteName.view_a_licence
