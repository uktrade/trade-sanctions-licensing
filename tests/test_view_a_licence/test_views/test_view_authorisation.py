from unittest.mock import patch

import pytest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse

from tests.factories import LicenceFactory


@pytest.mark.django_db
class TestApplicationListView:
    @patch("view_a_licence.mixins.send_email")
    def test_successful_view_application_list(self, mock_email, vl_client):
        test_user = User.objects.create_user(
            "John",
            "test@example.com",
            is_active=True,
        )
        vl_client.force_login(test_user)
        User.objects.create_user("Polly", "staff@example.com", is_staff=True, is_active=True)
        response = vl_client.get(reverse("view_a_licence:application_list"))
        assert response.status_code == 200
        mock_email.assert_not_called()

    @patch("view_a_licence.mixins.send_email")
    def test_inactive_user_view_application_list(self, mock_email, vl_client):
        test_user = User.objects.create_user(
            "John",
            "test@example.com",
            is_active=False,
        )
        vl_client.force_login(test_user)

        User.objects.create_user("Polly", "staff@example.com", is_staff=True, is_active=True)

        response = vl_client.get(reverse("view_a_licence:application_list"))
        assert response.status_code == 401
        mock_email.assert_called_once()

    def test_anonymous_user(self, vl_client, licence):
        response = vl_client.get(reverse("view_a_licence:application_list"))

        # we should be redirected to the login page
        assert response.status_code == 302
        assert "login" in response.url


@pytest.mark.django_db
class TestViewApplicationView:
    @patch("view_a_licence.mixins.send_email")
    def test_successful_view_a_single_licence_application(self, mock_email, vl_client):
        test_user = User.objects.create_user(
            "John",
            "test@example.com",
            is_active=True,
        )
        vl_client.force_login(test_user)
        User.objects.create_user("Polly", "staff@example.com", is_staff=True, is_active=True)

        licence = LicenceFactory()
        response = vl_client.get(reverse("view_a_licence:view_application", kwargs={"pk": licence.pk}))
        assert response.status_code == 200
        mock_email.assert_not_called()

    @patch("view_a_licence.mixins.send_email")
    def test_inactive_user_view_a_single_licence_application(self, mock_email, vl_client):
        test_user = User.objects.create_user(
            "John",
            "test@example.com",
            is_active=False,
        )
        vl_client.force_login(test_user)

        User.objects.create_user("Polly", "staff@example.com", is_staff=True, is_active=True)

        licence = LicenceFactory()
        response = vl_client.get(reverse("view_a_licence:view_application", kwargs={"pk": licence.pk}))
        assert response.status_code == 401
        assert "Not authorised to" in response.content.decode()
        mock_email.assert_called_once()

    def test_anonymous_user(self, vl_client, licence):
        response = vl_client.get(reverse("view_a_licence:view_application", kwargs={"pk": licence.pk}))

        # we should be redirected to the login page
        assert response.status_code == 302
        assert "login" in response.url


class TestUserAdminView:
    def test_staff_user(self, vl_client):
        test_user = User.objects.create_user(
            "John",
            "email@example.com",
            is_active=True,
            is_staff=True,
        )
        vl_client.force_login(test_user)
        response = vl_client.get(reverse("view_a_licence:manage_users"))
        assert response.status_code == 200

    def test_unauthorised_user(self, vl_client):
        test_user = User.objects.create_user(
            "John",
            "email@example.com",
            is_active=True,
            is_staff=False,
        )

        vl_client.force_login(test_user)
        response = vl_client.get(reverse("view_a_licence:manage_users"))
        assert response.status_code == 401

    def test_anonymous_user(self, vl_client):
        response = vl_client.get(reverse("view_a_licence:manage_users"))

        # we should be redirected to the login page
        assert response.status_code == 302
        assert "login" in response.url


def test_all_views_require_login():
    # gets all views from view_a_licence and asserts that they all require login
    from view_a_licence.urls import urlpatterns

    views = []
    for pattern in urlpatterns:
        if hasattr(pattern.callback, "cls"):
            view = pattern.callback.cls
        elif hasattr(pattern.callback, "view_class"):
            view = pattern.callback.view_class
        else:
            view = pattern.callback
        views.append(view)

    for view in views:
        assert issubclass(view, LoginRequiredMixin)
