from apply_for_a_licence.choices import WhoDoYouWantTheLicenceToCoverChoices
from django.urls import reverse

from tests.factories import LicenceFactory


class TestStartView:
    def test_post_myself(self, authenticated_al_client):
        licence = LicenceFactory()

        response = authenticated_al_client.post(
            reverse("start", kwargs={"pk": licence.id}),
            data={"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.myself.value},
        )

        assert response.status_code == 302
        assert response.url == reverse("add_yourself")

    def test_post_business(self, authenticated_al_client):
        licence = LicenceFactory()
        response = authenticated_al_client.post(
            reverse("start", kwargs={"pk": licence.id}),
            data={"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.business.value},
        )

        assert response.status_code == 302
        assert response.url == reverse("are_you_third_party")
