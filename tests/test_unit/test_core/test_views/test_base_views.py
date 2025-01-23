from apply_for_a_licence.models import Licence
from django.urls import reverse


class TestBaseLicenceFormView:
    def test_incorrect_user_get_form_kwargs(self, authenticated_al_client):
        licence = Licence.objects.create(user=None)

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.get(
            reverse("your_details"),
        )

        assert response.status_code == 404

    def test_correct_user_get_form_kwargs(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(user=test_apply_user)

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.get(
            reverse("your_details"),
        )

        assert response.status_code == 200
