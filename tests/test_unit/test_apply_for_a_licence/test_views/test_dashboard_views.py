import datetime

from apply_for_a_licence.models import Licence
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from tests.factories import LicenceFactory


class TestDashboardView:
    def test_get(self, authenticated_al_client, test_apply_user):
        licences = LicenceFactory.create_batch(
            size=3,
            user=test_apply_user,
            status="draft",
        )

        response = authenticated_al_client.get(reverse("dashboard"))
        assert response.status_code == 200
        applications = response.context["applications"]
        assert applications.count() == 3
        for application in applications:
            assert application in licences
            assert application.status == "draft"
            assert application.user == test_apply_user

    def test_gets_submitted(self, authenticated_al_client, test_apply_user):
        submitted_licence = LicenceFactory(user=test_apply_user, status="submitted")
        draft_licence = LicenceFactory(user=test_apply_user, status="draft")

        response = authenticated_al_client.get(reverse("dashboard"))
        assert response.status_code == 200
        applications = response.context["applications"]
        assert applications.count() == 2
        assert draft_licence in applications
        assert submitted_licence in applications

    def test_get_no_applications(self, authenticated_al_client):
        response = authenticated_al_client.get(reverse("dashboard"))
        assert response.status_code == 200
        assert response.url == reverse("dashboard")

    def test_date_in_template(self, authenticated_al_client, test_apply_user):
        licence = LicenceFactory(user=test_apply_user, status="draft")
        response = authenticated_al_client.get(reverse("dashboard"))
        assert licence.get_date_till_deleted().strftime("%d %B %Y") in response.content.decode()

    def test_only_show_actions_on_draft(self, authenticated_al_client, test_apply_user):
        LicenceFactory(user=test_apply_user, status="submitted")
        response = authenticated_al_client.get(reverse("dashboard"))
        assert "Delete draft" not in response.content.decode()

    def test_delete_expired_applications(self, authenticated_al_client, test_apply_user):
        licence = LicenceFactory(user=test_apply_user, status="draft")
        expired_licence = LicenceFactory(user=test_apply_user, status="draft")
        expired_licence.created_at = datetime.datetime(
            year=2020, month=1, day=29, hour=12, minute=0, second=0, tzinfo=datetime.timezone.utc
        )
        expired_licence.save()

        response = authenticated_al_client.get(reverse("dashboard"))
        assert response.status_code == 200
        applications = response.context["applications"]
        assert applications.count() == 1
        assert applications.get() == licence

        assert not Licence.objects.filter(pk=expired_licence.pk).exists()


class TestNewApplicationView:
    def test_get_context_data(self, authenticated_al_client, test_apply_user):
        LicenceFactory(user=test_apply_user, status="draft")
        response = authenticated_al_client.get(reverse("new_application"))
        assert response.context["DRAFT_APPLICATION_EXPIRY_DAYS"] == settings.DRAFT_APPLICATION_EXPIRY_DAYS


class TestDeleteApplicationView:
    def test_normal_delete(self, authenticated_al_client, test_apply_user):
        licence = LicenceFactory(user=test_apply_user, status="draft")
        response = authenticated_al_client.post(reverse("delete_application", kwargs={"pk": licence.pk}))
        assert response.status_code == 302
        assert response.url == reverse("dashboard")
        assert not Licence.objects.filter(pk=licence.pk).exists()

    def test_delete_submitted_application(self, authenticated_al_client, test_apply_user):
        licence = LicenceFactory(user=test_apply_user, status="submitted")
        response = authenticated_al_client.post(reverse("delete_application", kwargs={"pk": licence.pk}))
        assert response.status_code == 404
        assert Licence.objects.filter(pk=licence.pk).exists()

    def test_delete_not_your_own_application(self, authenticated_al_client, test_apply_user):
        another_user = User.objects.create(
            username="urn:fdc:another_user", first_name="Another", last_name="User", email="testnewuser@example.com"
        )
        licence = LicenceFactory(user=another_user, status="draft")
        response = authenticated_al_client.post(reverse("delete_application", kwargs={"pk": licence.pk}))
        assert response.status_code == 404
