from core.sites import is_apply_for_a_licence_site, is_view_a_licence_site
from django.contrib.auth.mixins import LoginRequiredMixin as DjangoLoginRequiredMixin
from django.urls import reverse


class LoginRequiredMixin(DjangoLoginRequiredMixin):
    def get_login_url(self):
        if is_apply_for_a_licence_site(self.request.site):
            # it's the public site, use GOV.UK One Login
            return reverse("authentication:login")
        elif is_view_a_licence_site(self.request.site):
            # it's the view-a-licence site, use Staff SSO
            return reverse("authbroker_client:login")
