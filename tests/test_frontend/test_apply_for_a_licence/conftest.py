import pytest


@pytest.fixture(autouse=True, scope="function")
def bypass_login(monkeypatch, test_apply_user):
    """Overrides the get_user function to always return the staff user without authentication.

    Effectively bypasses the login process for all frontend tests.
    """

    def patched_get_user(request):
        return test_apply_user

    monkeypatch.setattr("django.contrib.auth.get_user", patched_get_user)

    yield
