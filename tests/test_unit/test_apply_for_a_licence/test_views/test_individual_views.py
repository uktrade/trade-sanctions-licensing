import uuid

from apply_for_a_licence.choices import (
    NationalityAndLocation,
    TypeOfRelationshipChoices,
    WhoDoYouWantTheLicenceToCoverChoices,
)
from apply_for_a_licence.models import Individual, Organisation
from django.urls import reverse


class TestIndividualAddedView:
    def test_redirect_if_no_individual(self, authenticated_al_client):
        response = authenticated_al_client.get(
            reverse("individual_added"),
        )
        assert "individual-details" in response.url
        assert response.status_code == 302

    def test_do_not_add_individual_successful_post(self, authenticated_al_client, individual):

        response = authenticated_al_client.post(
            reverse("individual_added"),
            data={"do_you_want_to_add_another_individual": False},
        )
        assert response.url == reverse("business_employing_individual")

    def test_add_another_individual_successful_post(self, authenticated_al_client, individual):

        response = authenticated_al_client.post(
            reverse("individual_added"),
            data={"do_you_want_to_add_another_individual": True},
        )
        assert "individual-details" in response.url
        assert "?change=yes" in response.url

    def test_do_not_add_individual_myself_journey_successful_post(self, authenticated_al_client, yourself):
        response = authenticated_al_client.post(
            reverse("individual_added"),
            data={"do_you_want_to_add_another_individual": False},
        )
        assert response.url == reverse("tasklist")

    def test_get_context_data(self, authenticated_al_client, individual):
        response = authenticated_al_client.get(reverse("individual_added"))
        assert response.context["individuals"][0] == individual


class TestDeleteIndividualView:
    def test_successful_post(self, authenticated_al_client, individual_licence):
        individual1 = Individual.objects.create(licence=individual_licence)
        individual2 = Individual.objects.create(licence=individual_licence)
        all_individuals = Individual.objects.filter(licence=individual_licence)
        assert individual1 in all_individuals
        assert individual2 in all_individuals

        response = authenticated_al_client.post(
            reverse("delete_individual", kwargs={"pk": individual2.id}),
        )
        all_individuals = Individual.objects.filter(licence=individual_licence)
        assert individual1 in all_individuals
        assert individual2 not in all_individuals
        assert response.url == "/apply/add-individual"
        assert response.status_code == 302

    def test_cannot_delete_all_individuals_post(self, authenticated_al_client, individual_licence):
        individual1 = Individual.objects.create(licence=individual_licence)
        individual2 = Individual.objects.create(licence=individual_licence)
        individual3 = Individual.objects.create(licence=individual_licence)
        all_individuals = Individual.objects.filter(licence=individual_licence)
        assert individual1 in all_individuals
        assert individual2 in all_individuals
        assert individual3 in all_individuals
        authenticated_al_client.post(
            reverse("delete_individual", kwargs={"pk": individual1.id}),
        )
        authenticated_al_client.post(
            reverse("delete_individual", kwargs={"pk": individual2.id}),
        )
        # does not delete last individual
        response = authenticated_al_client.post(
            reverse("delete_individual", kwargs={"pk": individual3.id}),
        )
        all_individuals = Individual.objects.filter(licence=individual_licence)
        assert len(all_individuals) == 1
        assert individual1 not in all_individuals
        assert individual2 not in all_individuals
        assert individual3 in all_individuals
        assert response.status_code == 404

    def test_unsuccessful_post(self, authenticated_al_client, individual_licence):
        individual1 = Individual.objects.create(licence=individual_licence)
        individual2 = Individual.objects.create(licence=individual_licence)
        individual3 = Individual.objects.create(licence=individual_licence)
        all_individuals = Individual.objects.filter(licence=individual_licence)
        assert individual1 in all_individuals
        assert individual2 in all_individuals
        assert individual3 in all_individuals
        response = authenticated_al_client.post(
            reverse("delete_individual", kwargs={"pk": uuid.uuid4()}),
        )
        all_individuals = Individual.objects.filter(licence=individual_licence)
        assert len(all_individuals) == 3
        assert individual1 in all_individuals
        assert individual2 in all_individuals
        assert individual3 in all_individuals
        assert response.status_code == 404


class TestAddAnIndividualView:
    def test_redirect_after_post(self, authenticated_al_client, individual_licence):
        response = authenticated_al_client.post(
            reverse(
                "add_an_individual",
                kwargs={
                    "individual_uuid": uuid.uuid4(),
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

    def test_successful_post(self, authenticated_al_client, individual_licence):
        authenticated_al_client.post(
            reverse(
                "add_an_individual",
                kwargs={
                    "individual_uuid": uuid.uuid4(),
                },
            ),
            data={
                "first_name": "test",
                "last_name": "test last",
                "nationality_and_location": NationalityAndLocation.uk_national_uk_location.value,
            },
            follow=True,
        )

        individuals = Individual.objects.filter(licence=individual_licence)
        assert len(individuals) == 1
        individual1 = individuals.first()

        assert individual1.first_name == "test"
        assert individual1.last_name == "test last"
        assert individual1.nationality_and_location == NationalityAndLocation.uk_national_uk_location.value

        assert not individual1.country
        assert not individual1.address_line_1

    def test_get(self, authenticated_al_client, individual_licence):
        individual1 = Individual.objects.create(
            licence=individual_licence,
            first_name="Ben",
            last_name="Smith",
            nationality_and_location=NationalityAndLocation.dual_national_uk_location,
        )
        Individual.objects.create(
            licence=individual_licence,
            first_name="Test",
            last_name="User",
            nationality_and_location=NationalityAndLocation.uk_national_non_uk_location,
        )
        response = authenticated_al_client.get(
            reverse(
                "add_an_individual",
                kwargs={
                    "individual_uuid": individual1.id,
                },
            )
        )

        form = response.context["form"]
        assert form["first_name"].value() == "Ben"
        assert form["last_name"].value() == "Smith"
        assert form["nationality_and_location"].value() == NationalityAndLocation.dual_national_uk_location


class TestWhatIsIndividualsAddressView:
    def test_successful_post_uk_individual(self, authenticated_al_client, individual):
        assert not individual.country
        assert not individual.address_line_1
        assert not individual.county
        assert not individual.town_or_city
        assert not individual.postcode

        response = authenticated_al_client.post(
            reverse(
                "what_is_individuals_address",
                kwargs={"location": "in-uk", "individual_uuid": individual.id},
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
        individual = Individual.objects.get(id=individual.id)
        assert individual.country == "GB"
        assert individual.address_line_1 == "new address 1"
        assert individual.county == "Greater London"
        assert individual.town_or_city == "City"
        assert individual.postcode == "SW1A 1AA"

    def test_successful_post_non_uk_individual(self, authenticated_al_client, individual):
        assert not individual.country
        assert not individual.address_line_1
        assert not individual.county
        assert not individual.town_or_city
        assert not individual.postcode

        response = authenticated_al_client.post(
            reverse(
                "what_is_individuals_address",
                kwargs={"location": "outside-uk", "individual_uuid": individual.id},
            ),
            data={
                "country": "NL",
                "address_line_1": "Dutch address",
                "town_or_city": "Dutch City",
            },
        )

        assert response.url == reverse("individual_added")
        individual = Individual.objects.get(id=individual.id)
        assert individual.country == "NL"
        assert individual.address_line_1 == "Dutch address"
        assert individual.town_or_city == "Dutch City"

    def test_get_form_data(self, authenticated_al_client, individual):
        response = authenticated_al_client.get(
            reverse(
                "what_is_individuals_address",
                kwargs={
                    "location": "in-uk",
                    "individual_uuid": individual.id,
                },
            )
        )
        assert not response.context["form"].is_bound

    def test_get_success_url(self, authenticated_al_client, individual_licence, individual):
        individual_licence.who_do_you_want_the_licence_to_cover = WhoDoYouWantTheLicenceToCoverChoices.myself
        individual_licence.save()

        response = authenticated_al_client.post(
            reverse(
                "what_is_individuals_address",
                kwargs={
                    "location": "in-uk",
                    "individual_uuid": individual.id,
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


class TestBusinessEmployingIndividualView:
    def test_successful_get(self, authenticated_al_client, individual_licence):
        response = authenticated_al_client.get(reverse("business_employing_individual"))
        form = response.context["form"]
        assert form.form_h1_header == "Details of the business employing the individual"

    def test_form_h1_header_multiple_individuals(self, authenticated_al_client, individual_licence):
        Individual.objects.create(licence=individual_licence)
        Individual.objects.create(licence=individual_licence)
        response = authenticated_al_client.get(reverse("business_employing_individual"))
        form = response.context["form"]
        assert form.form_h1_header == "Details of the business employing the individuals"

    def test_save_form(self, authenticated_al_client, individual_licence):
        authenticated_al_client.post(
            reverse("business_employing_individual"),
            data={
                "name": "John Smith",
                "country": "GB",
                "address_line_1": "new address 1",
                "town_or_city": "City",
                "postcode": "SW1A 1AA",
            },
        )
        businesses = Organisation.objects.filter(
            licence=individual_licence, type_of_relationship=TypeOfRelationshipChoices.named_individuals
        )
        assert len(businesses) == 1
        assert businesses[0].status == "complete"
        assert businesses[0].name == "John Smith"
