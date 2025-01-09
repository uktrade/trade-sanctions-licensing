from authentication.mixins import LoginRequiredMixin
from django.urls import reverse


def test_public_login_required_middleware(apply_rf):
    mixin = LoginRequiredMixin()
    mixin.request = apply_rf
    assert mixin.get_login_url() == reverse("authentication:login")


def test_staff_login_required_middleware(viewer_rf):
    mixin = LoginRequiredMixin()
    mixin.request = viewer_rf
    assert mixin.get_login_url() == reverse("authbroker_client:login")
