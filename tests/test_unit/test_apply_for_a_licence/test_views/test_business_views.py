from django.test import RequestFactory
from django.urls import reverse

from . import data


class TestIsTheBusinessRegisteredWithCompaniesHouse:
    def test_business_not_registered_successful_post(self, authenticated_al_client):
        response = authenticated_al_client.post(
            reverse("is_the_business_registered_with_companies_house"),
            data={"business_registered_on_companies_house": "no"},
            follow=True,
        )
        assert reverse("where_is_the_business_located", kwargs=response.resolver_match.kwargs) in response.wsgi_request.path

    def test_business_registered_successful_post(self, authenticated_al_client):
        response = authenticated_al_client.post(
            reverse("is_the_business_registered_with_companies_house"), data={"business_registered_on_companies_house": "yes"}
        )
        assert response.url == reverse("do_you_know_the_registered_company_number")


class TestDoYouKnowTheRegisteredCompanyNumber:
    def test_know_the_registered_company_number_successful_post(self, authenticated_al_client):
        response = authenticated_al_client.post(
            reverse("do_you_know_the_registered_company_number"),
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
        )
        assert (
            reverse("do_you_know_the_registered_company_number", kwargs=response.resolver_match.kwargs)
            in response.wsgi_request.path
        )

    def test_do_not_know_the_registered_company_number_successful_post(self, authenticated_al_client):
        response = authenticated_al_client.post(
            reverse("do_you_know_the_registered_company_number"),
            data={"do_you_know_the_registered_company_number": "no"},
            follow=True,
        )
        assert reverse("where_is_the_business_located", kwargs=response.resolver_match.kwargs) in response.wsgi_request.path

    def test_get_context_data(self, authenticated_al_client):
        response = authenticated_al_client.get(reverse("do_you_know_the_registered_company_number"))
        assert response.context["page_title"] == "Registered Company Number"


class TestBusinessAddedView:
    def test_do_not_add_business_successful_post(self, authenticated_al_client):
        request = RequestFactory().get("/")
        request.session = authenticated_al_client.session
        request.session["businesses"] = data.businesses
        request.session.save()

        response = authenticated_al_client.post(
            reverse("business_added"),
            data={"do_you_want_to_add_another_business": False},
        )
        assert response.url == reverse("previous_licence")

    def test_add_another_business_successful_post(self, authenticated_al_client):
        request = RequestFactory().get("/")
        request.session = authenticated_al_client.session
        request.session["businesses"] = data.businesses
        request.session.save()

        response = authenticated_al_client.post(
            reverse("business_added"),
            data={"do_you_want_to_add_another_business": True},
        )
        assert response.url == reverse("is_the_business_registered_with_companies_house") + "?change=yes"


class TestDeleteBusinessView:
    def test_successful_post(self, authenticated_al_client):
        request = RequestFactory().post("/")
        request.session = authenticated_al_client.session
        request.session["businesses"] = data.businesses
        business_id = "business1"
        request.session.save()
        response = authenticated_al_client.post(
            reverse("delete_business"),
            data={"business_uuid": business_id},
        )
        assert "business1" not in authenticated_al_client.session["businesses"].keys()
        assert authenticated_al_client.session["businesses"] != data.businesses
        assert response.url == "/apply/add-business"
        assert response.status_code == 302

    def test_cannot_delete_all_businesses_post(self, authenticated_al_client):
        request = RequestFactory().post("/")
        request.session = authenticated_al_client.session
        request.session["businesses"] = data.businesses
        request.session.save()
        response = authenticated_al_client.post(
            reverse("delete_business"),
            data={"business_uuid": "business1"},
        )
        response = authenticated_al_client.post(
            reverse("delete_business"),
            data={"business_uuid": "business2"},
        )
        response = authenticated_al_client.post(
            reverse("delete_business"),
            data={"business_uuid": "business3"},
        )
        # does not delete last business
        assert len(authenticated_al_client.session["businesses"]) == 1
        assert "business3" in authenticated_al_client.session["businesses"].keys()
        assert response.url == "/apply/add-business"
        assert response.status_code == 302

    def test_unsuccessful_post(self, authenticated_al_client):
        request_object = RequestFactory().get("/")
        request_object.session = authenticated_al_client.session
        request_object.session["businesses"] = data.businesses
        request_object.session.save()
        response = authenticated_al_client.post(
            reverse("delete_business"),
        )
        assert authenticated_al_client.session["businesses"] == data.businesses
        assert response.url == "/apply/add-business"
        assert response.status_code == 302


class TestCheckCompanyDetailsView:
    def test_check_successful_post(self, request_object, authenticated_al_client):
        request_object.session = authenticated_al_client.session
        request_object.session["businesses"] = data.businesses
        request_object.session["companies_house_businesses"] = data.companies_house_business
        request_object.session.save()

        response = authenticated_al_client.post(reverse("check_company_details", kwargs={"business_uuid": "companieshouse1"}))
        businesses = authenticated_al_client.session["businesses"]
        assert response.url == "/apply/add-business"
        assert len(businesses) == 4
        assert "companieshouse1" in businesses.keys()

    def test_get_context_data(self, request_object, authenticated_al_client):
        request_object.session = authenticated_al_client.session
        request_object.session["businesses"] = data.businesses
        request_object.session["companies_house_businesses"] = data.companies_house_business
        request_object.session.save()

        response = authenticated_al_client.get(reverse("check_company_details", kwargs={"business_uuid": "companieshouse1"}))
        assert response.context["company_details"] == {
            "companies_house": True,
            "company_number": "1234567",
            "name": "Company 1",
            "readable_address": "AL1, United Kingdom",
        }
        assert response.context["business_uuid"] == "companieshouse1"
