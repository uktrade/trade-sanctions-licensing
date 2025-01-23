from apply_for_a_licence.choices import WhoDoYouWantTheLicenceToCoverChoices
from apply_for_a_licence.models import Licence
from django.test import RequestFactory
from django.urls import reverse


class TestSubmitterReferenceView:
    def test_post(self, authenticated_al_client):
        request = RequestFactory().get("/")
        request.session = authenticated_al_client.session
        response = authenticated_al_client.post(reverse("submitter_reference"))

        assert response.status_code == 302
        assert "start" in response.url
        assert response.url == reverse("start", kwargs={"pk": request.session["licence_id"]})


class TestStartView:
    def test_post_myself(self, authenticated_al_client):
        licence = Licence.objects.create()

        response = authenticated_al_client.post(
            reverse("start", kwargs={"pk": licence.id}),
            data={"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.myself.value},
        )

        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert licence_response.who_do_you_want_the_licence_to_cover == "myself"
        assert response.url == reverse("add_yourself")

    def test_post_business(self, authenticated_al_client):
        licence = Licence.objects.create()
        response = authenticated_al_client.post(
            reverse("start", kwargs={"pk": licence.id}),
            data={"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.business.value},
        )

        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert licence_response.who_do_you_want_the_licence_to_cover == "business"
        assert response.url == reverse("are_you_third_party")


class TestThirdPartyView:
    def test_post_third_party_individual(self, authenticated_al_client):
        licence = Licence.objects.create(
            who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.individual.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("are_you_third_party"),
            data={"is_third_party": True},
        )
        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert licence_response.is_third_party
        assert response.url == reverse("your_details")

    def test_post_third_party_business(self, authenticated_al_client):
        licence = Licence.objects.create(who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value)

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("are_you_third_party"),
            data={"is_third_party": True},
        )
        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert licence_response.is_third_party
        assert response.url == reverse("your_details")

    def test_post_not_third_party_individual(self, authenticated_al_client):
        licence = Licence.objects.create(
            who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.individual.value
        )
        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("are_you_third_party"),
            data={"is_third_party": False},
        )

        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert not licence_response.is_third_party
        assert "individual-details" in response.url

    def test_post_not_third_party_business(self, authenticated_al_client):
        licence = Licence.objects.create(who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value)

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("are_you_third_party"),
            data={"is_third_party": False},
        )

        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert not licence_response.is_third_party
        assert response.url == reverse("is_the_business_registered_with_companies_house")


class TestYourDetailsView:
    def test_post_individual(self, authenticated_al_client):
        licence = Licence.objects.create(
            is_third_party=True, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.individual.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("your_details"),
            data={"applicant_full_name": "John Smith", "applicant_business": "PBS", "applicant_role": "role 1"},
        )
        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert licence_response.applicant_role == "role 1"
        assert "individual-details" in response.url

    def test_post_business(self, authenticated_al_client):
        licence = Licence.objects.create(
            is_third_party=True, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("your_details"),
            data={"applicant_full_name": "John Smith", "applicant_business": "PBS", "applicant_role": "role 2"},
        )

        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert licence_response.applicant_role == "role 2"
        assert response.url == reverse("is_the_business_registered_with_companies_house")
