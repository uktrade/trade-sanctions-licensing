"""Authentication mechanisms for apply-for-a-licence"""

from authentication.backends import OneLoginBackend, StaffSSOBackend
from core.sites import is_apply_for_a_licence_site, is_view_a_licence_site
from django.contrib.auth import _clean_credentials
from django.contrib.auth.signals import user_login_failed
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.views.decorators.debug import sensitive_variables


class AuthenticationFailed(Exception):
    pass


def get_authentication_backend(request: HttpRequest) -> tuple[str, OneLoginBackend] | tuple[str, StaffSSOBackend]:
    """Gets the appropriate authentication backend for the given request"""
    if is_apply_for_a_licence_site(request.site):
        return "authentication.backends.OneLoginBackend", OneLoginBackend()
    elif is_view_a_licence_site(request.site):
        return "view_a_licence.auth_backends.StaffSSOBackend", StaffSSOBackend()


@sensitive_variables("credentials")
def authenticate(request=None, **credentials):
    """
    If the given credentials are valid, return a User object.
    """
    if not request:
        raise ValueError("authenticate() must be called with a request object")

    backend_path, backend = get_authentication_backend(request)
    try:
        try:
            user = backend.authenticate(request=request)
        except PermissionDenied:
            # This backend says to stop in our tracks - this user should not be
            # allowed in at all.
            raise AuthenticationFailed("Permission denied.")
        if user is None:
            raise AuthenticationFailed("Invalid credentials.")

        # Annotate the user object with the path of the backend.
        user.backend = backend_path
        return user
    except AuthenticationFailed as e:
        # The credentials supplied are invalid to all backends, fire signal
        user_login_failed.send(sender=__name__, credentials=_clean_credentials(credentials), request=request)
        raise e
