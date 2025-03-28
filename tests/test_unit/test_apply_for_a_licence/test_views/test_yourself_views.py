from apply_for_a_licence.choices import NationalityAndLocation
from apply_for_a_licence.models import Individual
from django.urls import reverse

from tests.factories import LicenceFactory


class TestYourselfAndIndividualAddedView:
    def test_do_not_add_another_individual_successful_post(self, authenticated_al_client, yourself):
        response = authenticated_al_client.post(
            reverse("yourself_and_individual_added"),
            data={"do_you_want_to_add_another_individual": False},
        )
        assert response.url == reverse("tasklist")
        assert response.status_code == 302

    def test_add_another_individual_successful_post(self, authenticated_al_client, yourself):
        response = authenticated_al_client.post(
            reverse("yourself_and_individual_added"),
            data={"do_you_want_to_add_another_individual": True},
        )
        assert "individual-details" in response.url
        assert response.status_code == 302


class TestAddYourselfView:
    def test_successful_post(self, authenticated_al_client, yourself):
        response = authenticated_al_client.post(
            reverse("add_yourself", kwargs={"yourself_uuid": yourself.id}),
            data={
                "first_name": "John",
                "last_name": "Doe",
                "nationality_and_location": NationalityAndLocation.uk_national_uk_location.value,
            },
            follow=True,
        )

        assert (
            reverse(
                "add_yourself_address",
                kwargs={"location": "in-uk", "yourself_uuid": yourself.id},
            )
            in response.redirect_chain[0][0]
        )
        yourself = Individual.objects.get(id=yourself.id)
        assert yourself.first_name == "John"
        assert yourself.nationality_and_location == NationalityAndLocation.uk_national_uk_location

    def test_is_applicant(self, authenticated_al_client_with_licence, yourself):
        yourself.is_applicant = False
        yourself.save()
        assert not yourself.is_applicant

        authenticated_al_client_with_licence.post(
            reverse("add_yourself", kwargs={"yourself_uuid": yourself.id}),
            data={
                "first_name": "John",
                "last_name": "Doe",
                "nationality_and_location": NationalityAndLocation.uk_national_uk_location.value,
            },
            follow=True,
        )

        yourself.refresh_from_db()
        assert yourself.is_applicant


class TestAddYourselfAddressView:
    def test_successful_non_uk_address_post(self, authenticated_al_client, yourself):
        response = authenticated_al_client.post(
            reverse(
                "add_yourself_address",
                kwargs={"location": "outside-uk", "yourself_uuid": yourself.id},
            ),
            data={
                "country": "DE",
                "town_or_city": "Berlin",
                "address_line_1": "Checkpoint Charlie",
                "nationality_and_location": NationalityAndLocation.non_uk_national_uk_location.value,
            },
        )

        assert response.url == reverse("yourself_and_individual_added")
        yourself = Individual.objects.get(id=yourself.id)
        assert yourself.country == "DE"
        assert yourself.address_line_1 == "Checkpoint Charlie"


class TestDeleteIndividualFromYourselfView:
    def test_successful_post(self, authenticated_al_client, yourself_licence, yourself):
        individual1 = Individual.objects.create(licence=yourself_licence)
        individual2 = Individual.objects.create(licence=yourself_licence)

        response = authenticated_al_client.post(
            reverse("delete_individual_from_yourself", kwargs={"pk": individual1.id}),
        )
        individuals = Individual.objects.filter(licence=yourself_licence)
        assert individual1 not in individuals
        assert individual2 in individuals
        assert yourself in individuals
        assert response.url == "/apply/check-your-details-add-individuals"
        assert response.status_code == 302

    def test_delete_all_individuals_post(self, authenticated_al_client, yourself_licence, yourself):
        individual1 = Individual.objects.create(licence=yourself_licence)
        individual2 = Individual.objects.create(licence=yourself_licence)

        authenticated_al_client.post(
            reverse("delete_individual_from_yourself", kwargs={"pk": individual1.id}),
        )
        response = authenticated_al_client.post(
            reverse("delete_individual_from_yourself", kwargs={"pk": individual2.id}),
        )
        individuals = Individual.objects.filter(licence=yourself_licence)
        assert individual1 not in individuals
        assert individual2 not in individuals
        assert yourself in individuals
        assert response.url == "/apply/check-your-details-add-individuals"
        assert response.status_code == 302

    def test_unsuccessful_post(self, authenticated_al_client, yourself_licence, yourself):
        individual1 = Individual.objects.create(licence=yourself_licence)
        individual2 = Individual.objects.create(licence=yourself_licence)

        new_licence = LicenceFactory()
        individual3 = Individual.objects.create(licence=new_licence)
        response = authenticated_al_client.post(
            reverse("delete_individual_from_yourself", kwargs={"pk": individual3.pk}),
        )

        individuals = Individual.objects.filter(licence=yourself_licence)
        assert individual1 in individuals
        assert individual2 in individuals
        assert yourself in individuals
        assert response.status_code == 404
