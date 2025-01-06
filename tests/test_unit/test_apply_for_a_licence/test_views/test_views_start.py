from apply_for_a_licence.choices import WhoDoYouWantTheLicenceToCoverChoices
from django.urls import reverse


class TestStartView:
    def test_post_myself(self, authenticated_al_client):
        response = authenticated_al_client.post(
            reverse("start"),
            data={"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.myself.value},
        )

        assert response.status_code == 302
        assert response.url == reverse("what_is_your_email")

    def test_post_business(self, authenticated_al_client):
        response = authenticated_al_client.post(
            reverse("start"),
            data={"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.business.value},
        )

        assert response.status_code == 302
        assert response.url == reverse("are_you_third_party")
