from core.sites import is_apply_for_a_licence_site, is_view_a_licence_site
from django.contrib.auth.mixins import LoginRequiredMixin as DjangoLoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse


class AuthenticatedAnonymousUser(AnonymousUser):
    @property
    def is_authenticated(self):
        return True


class LoginRequiredMixin(DjangoLoginRequiredMixin):
    """def dispatch(self, request: HttpRequest, *args, **kwargs):
    if is_apply_for_a_licence_site(request.site):
        # we're currently not enforcing one-login for the apply site
        request.user = AuthenticatedAnonymousUser()
    return super().dispatch(request, *args, **kwargs)"""

    def get_login_url(self):
        if is_apply_for_a_licence_site(self.request.site):
            # it's the public site, use GOV.UK One Login
            return reverse("authentication:login")
        elif is_view_a_licence_site(self.request.site):
            # it's the view-a-licence site, use Staff SSO
            return reverse("authbroker_client:login")
