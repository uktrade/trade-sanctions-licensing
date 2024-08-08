from django.test import RequestFactory
from django.urls import reverse

from . import data


class TestBusinessAddedView:
    def test_do_not_add_business_successful_post(self, afal_client):
        request = RequestFactory().get("/")
        request.session = afal_client.session
        request.session["businesses"] = data.businesses
        request.session.save()

        response = afal_client.post(
            reverse("business_added"),
            data={"do_you_want_to_add_another_business": False},
        )
        assert response.url == reverse("previous_licence")

    def test_add_another_business_successful_post(self, afal_client):
        request = RequestFactory().get("/")
        request.session = afal_client.session
        request.session["businesses"] = data.businesses
        request.session.save()

        response = afal_client.post(
            reverse("business_added"),
            data={"do_you_want_to_add_another_business": True},
        )
        assert response.url == reverse("is_the_business_registered_with_companies_house")


class TestDeleteBusinessView:
    def test_successful_post(self, afal_client):
        request = RequestFactory().post("/")
        request.session = afal_client.session
        request.session["businesses"] = data.businesses
        business_id = "business1"
        request.session.save()
        response = afal_client.post(
            reverse("delete_business"),
            data={"business_uuid": business_id},
        )
        assert "business1" not in afal_client.session["businesses"].keys()
        assert afal_client.session["businesses"] != data.businesses
        assert response.url == "/apply-for-a-licence/business_added"
        assert response.status_code == 302

    def test_cannot_delete_all_businesses_post(self, afal_client):
        request = RequestFactory().post("/")
        request.session = afal_client.session
        request.session["businesses"] = data.businesses
        request.session.save()
        response = afal_client.post(
            reverse("delete_business"),
            data={"business_uuid": "business1"},
        )
        response = afal_client.post(
            reverse("delete_business"),
            data={"business_uuid": "business2"},
        )
        response = afal_client.post(
            reverse("delete_business"),
            data={"business_uuid": "business3"},
        )
        # does not delete last business
        assert len(afal_client.session["businesses"]) == 1
        assert "business3" in afal_client.session["businesses"].keys()
        assert response.url == "/apply-for-a-licence/business_added"
        assert response.status_code == 302

    def test_unsuccessful_post(self, afal_client):
        request_object = RequestFactory().get("/")
        request_object.session = afal_client.session
        request_object.session["businesses"] = data.businesses
        request_object.session.save()
        response = afal_client.post(
            reverse("delete_business"),
        )
        assert afal_client.session["businesses"] == data.businesses
        assert response.url == "/apply-for-a-licence/business_added"
        assert response.status_code == 302
