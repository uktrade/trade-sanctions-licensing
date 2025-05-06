from apply_for_a_licence.choices import WhoDoYouWantTheLicenceToCoverChoices
from apply_for_a_licence.models import Licence
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.urls import reverse


class TestTriageView:
    def test_get(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user,
        )
        response = authenticated_al_client.get(reverse("triage", kwargs={"licence_pk": licence.id}))
        assert response.status_code == 302
        assert response.url == reverse("tasklist", kwargs={"licence_pk": licence.id})

    def test_incorrect_user_raises_error(self, authenticated_al_client, test_apply_user):
        user, created = User.objects.get_or_create(
            username="urn:fdc:test_other_user",
            defaults={
                "first_name": "Other",
                "last_name": "Test",
                "email": "apply_other_user@example.com",
                "is_active": True,
                "is_staff": False,
                "password": "password",
            },
        )
        public_group = Group.objects.get(name=settings.PUBLIC_USER_GROUP_NAME)
        user.groups.add(public_group)
        licence = Licence.objects.create(
            user=user,
        )
        session = authenticated_al_client.session
        session.update({"licence_id": licence.id})
        session.save()
        response = authenticated_al_client.get(reverse("triage", kwargs={"licence_pk": licence.id}))
        assert response.status_code == 400


class TestTaskListView:
    def test_get_licence_without_journey_type(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user,
        )
        response = authenticated_al_client.get(reverse("tasklist", kwargs={"licence_pk": licence.id}))
        assert response.status_code == 302
        assert response.url == reverse("start", kwargs={"licence_pk": licence.id})

    def test_get_licence_with_journey_type(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.individual.value
        )
        response = authenticated_al_client.get(reverse("tasklist", kwargs={"licence_pk": licence.id}))
        assert response.status_code == 200
        licence_response = response.context["licence"]
        assert licence_response == licence
        assert licence_response.who_do_you_want_the_licence_to_cover == WhoDoYouWantTheLicenceToCoverChoices.individual.value
