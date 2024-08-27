from django.test import RequestFactory
from django.urls import reverse

from . import data


class TestYourselfAndIndividualAddedView:
    def test_do_not_add_another_individual_successful_post(self, al_client):
        request = RequestFactory().get("/")
        request.session = al_client.session
        request.session["individuals"] = data.individuals
        request.session.save()
        response = al_client.post(
            reverse("yourself_and_individual_added"),
            data={"do_you_want_to_add_another_individual": False},
        )
        assert response.url == reverse("previous_licence")
        assert response.status_code == 302

    def test_add_another_individual_successful_post(self, al_client):
        request = RequestFactory().get("/")
        request.session = al_client.session
        request.session["individuals"] = data.individuals
        request.session.save()
        response = al_client.post(
            reverse("yourself_and_individual_added"),
            data={"do_you_want_to_add_another_individual": True},
        )
        assert response.url == reverse("add_an_individual") + "?change=yes"
        assert response.status_code == 302


class TestAddYourselfView:
    def test_successful_uk_post(self, al_client):
        response = al_client.post(
            reverse("add_yourself"),
            data={"first_name": "John", "last_name": "Doe", "nationality_and_location": "uk_national_uk_location"},
        )
        assert response.url == reverse("add_yourself_address_uk")

    def test_successful_non_uk_post(self, al_client):
        response = al_client.post(
            reverse("add_yourself"),
            data={"first_name": "John", "last_name": "Doe", "nationality_and_location": "uk_national_non_uk_location"},
        )
        assert response.url == reverse("add_yourself_address_non_uk")


class TestAddYourselfUKAddressView:
    def test_successful_non_uk_address_post(self, al_client):
        response = al_client.post(
            reverse("add_yourself_address_uk"),
            data={"country": "GB", "town_or_city": "London", "address_line_1": "Buck Pal", "postcode": "AA1 1AA"},
        )
        assert response.url == reverse("yourself_and_individual_added")


class TestAddYourselfNonUKAddressView:
    def test_successful_non_uk_address_post(self, al_client):
        response = al_client.post(
            reverse("add_yourself_address_non_uk"),
            data={"country": "DE", "town_or_city": "Berlin", "address_line_1": "Checkpoint Charlie"},
        )
        assert response.url == reverse("yourself_and_individual_added")


class TestDeleteIndividualFromYourselfView:
    def test_successful_post(self, al_client):
        request = RequestFactory().post("/")
        request.session = al_client.session
        request.session["individuals"] = data.individuals
        individual_id = "individual1"
        request.session.save()
        response = al_client.post(
            reverse("delete_individual_from_yourself"),
            data={"individual_uuid": individual_id},
        )
        assert "individual1" not in al_client.session["individuals"].keys()
        assert al_client.session["individuals"] != data.individuals
        assert response.url == "/apply-for-a-licence/yourself_and_individual_added"
        assert response.status_code == 302

    def test_delete_all_individuals_post(self, al_client):
        request = RequestFactory().post("/")
        request.session = al_client.session
        request.session["individuals"] = data.individuals
        request.session.save()
        response = al_client.post(
            reverse("delete_individual_from_yourself"),
            data={"individual_uuid": "individual1"},
        )
        response = al_client.post(
            reverse("delete_individual_from_yourself"),
            data={"individual_uuid": "individual2"},
        )
        response = al_client.post(
            reverse("delete_individual_from_yourself"),
            data={"individual_uuid": "individual3"},
        )
        # does not delete last individual
        assert len(al_client.session["individuals"]) == 0
        assert response.url == "/apply-for-a-licence/yourself_and_individual_added"
        assert response.status_code == 302

    def test_unsuccessful_post(self, al_client):
        request_object = RequestFactory().get("/")
        request_object.session = al_client.session
        request_object.session["individuals"] = data.individuals
        request_object.session.save()
        response = al_client.post(
            reverse("delete_individual_from_yourself"),
        )
        assert al_client.session["individuals"] == data.individuals
        assert response.url == "/apply-for-a-licence/yourself_and_individual_added"
        assert response.status_code == 302
