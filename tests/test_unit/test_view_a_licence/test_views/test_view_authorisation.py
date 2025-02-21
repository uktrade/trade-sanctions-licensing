from unittest.mock import patch

import pytest
from apply_for_a_licence.choices import WhoDoYouWantTheLicenceToCoverChoices
from authentication.mixins import GroupsRequiredMixin, LoginRequiredMixin
from authentication.utils import get_group
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from tests.factories import LicenceFactory


@pytest.mark.django_db
class TestApplicationListView:
    @patch("view_a_licence.mixins.send_email")
    def test_successful_view_application_list(self, mock_email, vl_client):
        admin_user = User.objects.create_user("Polly", "staff@example.com", is_staff=True, is_active=True)
        admin_user.groups.add(get_group(settings.ADMIN_USER_GROUP_NAME))

        test_user = User.objects.create_user(
            "John",
            "test@example.com",
            is_active=True,
        )
        test_user.groups.add(get_group(settings.INTERNAL_USER_GROUP_NAME))
        vl_client.force_login(test_user, backend="authentication.backends.StaffSSOBackend")
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
        vl_client.force_login(test_user, backend="authentication.backends.StaffSSOBackend")

        admin_user = User.objects.create_user("Polly", "staff@example.com", is_active=True)
        admin_user.groups.add(get_group(settings.ADMIN_USER_GROUP_NAME))

        response = vl_client.get(reverse("view_a_licence:application_list"))
        assert response.status_code == 403
        mock_email.assert_called_once()

    def test_anonymous_user(self, vl_client, licence):
        response = vl_client.get(reverse("view_a_licence:application_list"))

        # we should be redirected to the login page
        assert response.status_code == 302
        assert reverse("authbroker_client:login") in response.url


@pytest.mark.django_db
class TestViewApplicationView:
    @patch("view_a_licence.mixins.send_email")
    def test_successful_view_a_single_licence_application(self, mock_email, vl_client):
        test_user = User.objects.create_user(
            "John",
            "test@example.com",
            is_active=True,
        )
        test_user.groups.add(get_group(settings.INTERNAL_USER_GROUP_NAME))
        vl_client.force_login(test_user, backend="authentication.backends.StaffSSOBackend")
        admin_user = User.objects.create_user("Polly", "staff@example.com", is_active=True)
        admin_user.groups.add(get_group(settings.ADMIN_USER_GROUP_NAME))

        licence = LicenceFactory(
            who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value,
            status="submitted",
        )
        response = vl_client.get(reverse("view_a_licence:view_application", kwargs={"reference": licence.reference}))
        assert response.status_code == 200
        mock_email.assert_not_called()

    @patch("view_a_licence.mixins.send_email")
    def test_inactive_user_view_a_single_licence_application(self, mock_email, vl_client):
        test_user = User.objects.create_user(
            "John",
            "test@example.com",
            is_active=False,
        )
        vl_client.force_login(test_user, backend="authentication.backends.StaffSSOBackend")

        admin_user = User.objects.create_user("Polly", "staff@example.com", is_active=True)
        admin_user.groups.add(get_group(settings.ADMIN_USER_GROUP_NAME))

        licence = LicenceFactory()
        response = vl_client.get(reverse("view_a_licence:view_application", kwargs={"reference": licence.reference}))
        assert response.status_code == 403
        assert "Not authorised to" in response.content.decode()
        mock_email.assert_called_once()

    def test_anonymous_user(self, vl_client, licence):
        response = vl_client.get(reverse("view_a_licence:view_application", kwargs={"reference": licence.reference}))

        # we should be redirected to the login page
        assert response.status_code == 302
        assert reverse("authbroker_client:login") in response.url


class TestUserAdminView:
    def test_staff_user(self, vl_client):
        test_user = User.objects.create_user(
            "John",
            "email@example.com",
            is_active=True,
            is_staff=True,
        )
        test_user.groups.add(get_group(settings.ADMIN_USER_GROUP_NAME))
        vl_client.force_login(test_user, backend="authentication.backends.StaffSSOBackend")
        response = vl_client.get(reverse("view_a_licence:manage_users"))
        assert response.status_code == 200

    def test_unauthorised_user(self, vl_client):
        test_user = User.objects.create_user(
            "John",
            "email@example.com",
            is_active=True,
            is_staff=False,
        )

        vl_client.force_login(test_user, backend="authentication.backends.StaffSSOBackend")
        response = vl_client.get(reverse("view_a_licence:manage_users"))
        assert response.status_code == 403

    def test_anonymous_user(self, vl_client):
        response = vl_client.get(reverse("view_a_licence:manage_users"))

        # we should be redirected to the login page
        assert response.status_code == 302
        assert reverse("authbroker_client:login") in response.url


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
        assert issubclass(view, GroupsRequiredMixin)

        admin_only = settings.ADMIN_USER_GROUP_NAME in view.groups_required
        internal_only = settings.INTERNAL_USER_GROUP_NAME in view.groups_required

        # we need at least one of the above as well
        assert admin_only or internal_only
