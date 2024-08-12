from django.test import RequestFactory
from django.urls import reverse

from . import data


class TestIsTheBusinessRegisteredWithCompaniesHouse:
    def test_business_not_registered_successful_post(self, al_client):
        response = al_client.post(
            reverse("is_the_business_registered_with_companies_house"), data={"business_registered_on_companies_house": "no"}
        )
        assert response.url == reverse("where_is_the_business_located")

    def test_business_registered_successful_post(self, al_client):
        response = al_client.post(
            reverse("is_the_business_registered_with_companies_house"), data={"business_registered_on_companies_house": "yes"}
        )
        assert response.url == reverse("do_you_know_the_registered_company_number")


class TestDoYouKnowTheRegisteredCompanyNumber:
    def test_know_the_registered_company_number_successful_post(self, al_client):
        pass

    def test_do_not_know_the_registered_company_number_successful_post(self, al_client):
        response = al_client.post(
            reverse("do_you_know_the_registered_company_number"), data={"do_you_know_the_registered_company_number": "no"}
        )
        assert response.url == reverse("where_is_the_business_located")


class TestBusinessAddedView:
    def test_do_not_add_business_successful_post(self, al_client):
        request = RequestFactory().get("/")
        request.session = al_client.session
        request.session["businesses"] = data.businesses
        request.session.save()

        response = al_client.post(
            reverse("business_added"),
            data={"do_you_want_to_add_another_business": False},
        )
        assert response.url == reverse("previous_licence")

    def test_add_another_business_successful_post(self, al_client):
        request = RequestFactory().get("/")
        request.session = al_client.session
        request.session["businesses"] = data.businesses
        request.session.save()

        response = al_client.post(
            reverse("business_added"),
            data={"do_you_want_to_add_another_business": True},
        )
        assert response.url == reverse("is_the_business_registered_with_companies_house") + "?change=yes"


class TestDeleteBusinessView:
    def test_successful_post(self, al_client):
        request = RequestFactory().post("/")
        request.session = al_client.session
        request.session["businesses"] = data.businesses
        business_id = "business1"
        request.session.save()
        response = al_client.post(
            reverse("delete_business"),
            data={"business_uuid": business_id},
        )
        assert "business1" not in al_client.session["businesses"].keys()
        assert al_client.session["businesses"] != data.businesses
        assert response.url == "/apply-for-a-licence/business_added"
        assert response.status_code == 302

    def test_cannot_delete_all_businesses_post(self, al_client):
        request = RequestFactory().post("/")
        request.session = al_client.session
        request.session["businesses"] = data.businesses
        request.session.save()
        response = al_client.post(
            reverse("delete_business"),
            data={"business_uuid": "business1"},
        )
        response = al_client.post(
            reverse("delete_business"),
            data={"business_uuid": "business2"},
        )
        response = al_client.post(
            reverse("delete_business"),
            data={"business_uuid": "business3"},
        )
        # does not delete last business
        assert len(al_client.session["businesses"]) == 1
        assert "business3" in al_client.session["businesses"].keys()
        assert response.url == "/apply-for-a-licence/business_added"
        assert response.status_code == 302

    def test_unsuccessful_post(self, al_client):
        request_object = RequestFactory().get("/")
        request_object.session = al_client.session
        request_object.session["businesses"] = data.businesses
        request_object.session.save()
        response = al_client.post(
            reverse("delete_business"),
        )
        assert al_client.session["businesses"] == data.businesses
        assert response.url == "/apply-for-a-licence/business_added"
        assert response.status_code == 302
