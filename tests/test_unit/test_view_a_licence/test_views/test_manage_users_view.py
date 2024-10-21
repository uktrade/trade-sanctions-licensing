from django.contrib.auth.models import User
from django.urls import reverse

from tests.factories import UserFactory


class TestManageUsersView:
    def test_get_context_data(self, vl_client_logged_in, staff_user):
        inactive_user = UserFactory.create(is_active=False, is_staff=False)

        response = vl_client_logged_in.get(reverse("view_a_licence:manage_users"))
        assert response.context["pending_users"].count() == 1
        assert response.context["pending_users"].first() == inactive_user
        assert response.context["accepted_users"].count() == 1
        assert response.context["accepted_users"].first() == staff_user

    def test_make_active(self, vl_client_logged_in):
        inactive_user = UserFactory.create(is_active=False, is_staff=False)

        response = vl_client_logged_in.get(reverse("view_a_licence:manage_users") + f"?accept_user={inactive_user.id}")
        assert response.status_code == 302
        assert response.url == reverse("view_a_licence:manage_users")

        inactive_user.refresh_from_db()
        assert inactive_user.is_active

    def test_delete_user(self, vl_client_logged_in):
        active_user = UserFactory.create(is_active=True, is_staff=True)

        response = vl_client_logged_in.get(reverse("view_a_licence:manage_users") + f"?delete_user={active_user.id}")
        assert response.status_code == 302
        assert response.url == reverse("view_a_licence:manage_users")

        assert not User.objects.filter(id=active_user.id).exists()
