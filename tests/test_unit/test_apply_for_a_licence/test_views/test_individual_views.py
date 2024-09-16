from apply_for_a_licence.choices import (
    NationalityAndLocation,
    WhoDoYouWantTheLicenceToCoverChoices,
)
from django.test import RequestFactory
from django.urls import reverse

from . import data


class TestIndividualAddedView:
    def test_do_not_add_individual_successful_post(self, al_client):
        request = RequestFactory().get("/")
        request.session = al_client.session
        request.session["individuals"] = data.individuals
        request.session.save()

        response = al_client.post(
            reverse("individual_added"),
            data={"do_you_want_to_add_another_individual": False},
        )
        assert response.url == reverse("previous_licence")

    def test_add_another_individual_successful_post(self, al_client):
        request = RequestFactory().get("/")
        request.session = al_client.session
        request.session["individuals"] = data.individuals
        request.session.save()

        response = al_client.post(
            reverse("individual_added"),
            data={"do_you_want_to_add_another_individual": True},
        )
        assert (
            response.url
            == reverse(
                "add_an_individual",
                kwargs={
                    "individual_uuid": "individual2",
                },
            )
            + "?change=yes"
        )


class TestDeleteIndividualView:
    def test_successful_post(self, al_client):
        request = RequestFactory().post("/")
        request.session = al_client.session
        request.session["individuals"] = data.individuals
        individual_id = "individual1"
        request.session.save()
        response = al_client.post(
            reverse("delete_individual"),
            data={"individual_uuid": individual_id},
        )
        assert "individual1" not in al_client.session["individuals"].keys()
        assert al_client.session["individuals"] != data.individuals
        assert response.url == "/apply-for-a-licence/individual_added"
        assert response.status_code == 302

    def test_cannot_delete_all_individuals_post(self, al_client):
        request = RequestFactory().post("/")
        request.session = al_client.session
        request.session["individuals"] = data.individuals
        request.session.save()
        response = al_client.post(
            reverse("delete_individual"),
            data={"individual_uuid": "individual1"},
        )
        response = al_client.post(
            reverse("delete_individual"),
            data={"individual_uuid": "individual2"},
        )
        response = al_client.post(
            reverse("delete_individual"),
            data={"individual_uuid": "individual3"},
        )
        # does not delete last individual
        assert len(al_client.session["individuals"]) == 1
        assert "individual3" in al_client.session["individuals"].keys()
        assert response.url == "/apply-for-a-licence/individual_added"
        assert response.status_code == 302

    def test_unsuccessful_post(self, al_client):
        request_object = RequestFactory().get("/")
        request_object.session = al_client.session
        request_object.session["individuals"] = data.individuals
        request_object.session.save()
        response = al_client.post(
            reverse("delete_individual"),
        )
        assert al_client.session["individuals"] == data.individuals
        assert response.url == "/apply-for-a-licence/individual_added"
        assert response.status_code == 302


class TestAddAnIndividualView:
    def test_redirect_after_post(self, al_client):
        response = al_client.post(
            reverse(
                "add_an_individual",
                kwargs={
                    "individual_uuid": "individual1",
                },
            )
            + "?redirect_to_url=check_your_answers&new=yes",
            data={
                "first_name": "test",
                "last_name": "test last",
                "nationality_and_location": NationalityAndLocation.uk_national_uk_location.value,
            },
            follow=True,
        )
        assert (
            reverse(
                "what_is_individuals_address",
                kwargs={
                    "location": response.resolver_match.kwargs["location"],
                    "individual_uuid": response.resolver_match.kwargs["individual_uuid"],
                },
            )
            in response.redirect_chain[0][0]
        )

        # check that the query parameters are passed to the redirect
        assert "redirect_to_url=check_your_answers&new=yes" in response.redirect_chain[0][0]

    def test_successful_post(self, al_client):
        assert al_client.session.get("individuals") is None
        response = al_client.post(
            reverse(
                "add_an_individual",
                kwargs={
                    "individual_uuid": "individual1",
                },
            ),
            data={
                "first_name": "test",
                "last_name": "test last",
                "nationality_and_location": NationalityAndLocation.uk_national_uk_location.value,
            },
            follow=True,
        )

        individual_uuid = response.resolver_match.kwargs["individual_uuid"]
        individuals = al_client.session.get("individuals")
        assert len(individuals) == 1

        assert individuals[individual_uuid]["name_data"]["cleaned_data"]["first_name"] == "test"
        assert individuals[individual_uuid]["name_data"]["cleaned_data"]["last_name"] == "test last"
        assert (
            individuals[individual_uuid]["name_data"]["cleaned_data"]["nationality_and_location"]
            == NationalityAndLocation.uk_national_uk_location.value
        )
        assert (
            individuals[individual_uuid]["name_data"]["cleaned_data"]["nationality"]
            == NationalityAndLocation.uk_national_uk_location.label
        )

        assert individuals[individual_uuid].get("address_data") is None

    def test_get(self, al_client):
        session = al_client.session
        session["individuals"] = data.individuals
        session.save()

        response = al_client.get(
            reverse(
                "add_an_individual",
                kwargs={
                    "individual_uuid": "individual1",
                },
            ),
        )
        form = response.context["form"]

        assert form.data["first_name"] == "Recipient"
        assert form.data["last_name"] == "1"
        assert form.data["nationality_and_location"] == NationalityAndLocation.uk_national_uk_location.value


class TestWhatIsIndividualsAddressView:
    def test_successful_post(self, al_client):
        session = al_client.session
        session["individuals"] = data.individuals
        session.save()

        response = al_client.post(
            reverse(
                "what_is_individuals_address",
                kwargs={
                    "location": "in_the_uk",
                    "individual_uuid": "individual1",
                },
            ),
            data={
                "country": "GB",
                "address_line_1": "new address 1",
                "address_line_2": "new address 2",
                "county": "Greater London",
                "town_or_city": "City",
                "postcode": "SW1A 1AA",
            },
        )

        assert response.url == reverse("individual_added")

        individuals = al_client.session.get("individuals")
        assert len(individuals) == 3

        assert individuals["individual1"]["address_data"]["cleaned_data"]["country"] == "GB"
        assert individuals["individual1"]["address_data"]["cleaned_data"]["address_line_1"] == "new address 1"
        assert individuals["individual1"]["address_data"]["cleaned_data"]["county"] == "Greater London"
        assert individuals["individual1"]["address_data"]["cleaned_data"]["town_or_city"] == "City"
        assert individuals["individual1"]["address_data"]["cleaned_data"]["postcode"] == "SW1A 1AA"

    def test_get_form_data(self, al_client):
        response = al_client.get(
            reverse(
                "what_is_individuals_address",
                kwargs={
                    "location": "in_the_uk",
                    "individual_uuid": "individualNA",
                },
            )
        )
        assert not response.context["form"].is_bound

    def test_get_success_url(self, al_client):
        session = al_client.session
        session["start"] = {"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.myself.value}
        session["individuals"] = data.individuals
        session.save()

        response = al_client.post(
            reverse(
                "what_is_individuals_address",
                kwargs={
                    "location": "in_the_uk",
                    "individual_uuid": "individual1",
                },
            ),
            data={
                "country": "GB",
                "address_line_1": "new address 1",
                "address_line_2": "new address 2",
                "county": "Greater London",
                "town_or_city": "City",
                "postcode": "SW1A 1AA",
            },
        )

        assert response.url == reverse("yourself_and_individual_added")
