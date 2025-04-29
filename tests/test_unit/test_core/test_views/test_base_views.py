from apply_for_a_licence.models import Licence
from django.urls import reverse


class TestBaseLicenceFormView:
    def test_incorrect_user_get_form_kwargs(self, authenticated_al_client):
        licence = Licence.objects.create(user=None)

        response = authenticated_al_client.get(
            reverse("your_details", kwargs={"licence_pk": licence.id}),
        )

        assert response.status_code == 404

    def test_correct_user_get_form_kwargs(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(user=test_apply_user)

        response = authenticated_al_client.get(
            reverse("your_details", kwargs={"licence_pk": licence.id}),
        )

        assert response.status_code == 200


class TestRedirectBaseDomainView:
    def test_redirect_apply_site(self, authenticated_al_client):
        response = authenticated_al_client.get("/")
        assert response.status_code == 302
        assert response.url == reverse("dashboard")

    def test_redirect_view_site(self, vl_client_logged_in):
        response = vl_client_logged_in.get("/")
        assert response.status_code == 302
        assert response.url == reverse("view_a_licence:application_list")
