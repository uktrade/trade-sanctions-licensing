from django.test import RequestFactory
from django.urls import reverse

from . import data


class TestIndividualAddedView:
    def test_successful_post(self, afal_client):
        request = RequestFactory().post("/")
        request.session = afal_client.session
        request.session.save()

        response = afal_client.post(
            reverse("individual_added"),
            data={},
        )
        assert response.url == reverse("previous_licence")
        assert response.status_code == 201


class TestDeleteIndividualView:
    def test_successful_post(self, afal_client):
        request = RequestFactory().post("/")
        request.session = afal_client.session
        request.session["individuals"] = data.individuals
        individual_id = "individual1"
        request.session.save()
        response = afal_client.post(
            reverse("delete_individual"),
            data={"individual_uuid": individual_id},
        )
        assert "individual1" not in afal_client.session["individuals"].keys()
        assert afal_client.session["individuals"] != data.individuals
        assert response.url == "/apply-for-a-licence/individual_added"
        assert response.status_code == 302

    def test_cannot_delete_all_individuals_post(self, afal_client):
        request = RequestFactory().post("/")
        request.session = afal_client.session
        request.session["individuals"] = data.individuals
        request.session.save()
        response = afal_client.post(
            reverse("delete_individual"),
            data={"individual_uuid": "individual1"},
        )
        response = afal_client.post(
            reverse("delete_individual"),
            data={"individual_uuid": "individual2"},
        )
        response = afal_client.post(
            reverse("delete_individual"),
            data={"individual_uuid": "individual3"},
        )
        # does not delete last individual
        assert len(afal_client.session["individuals"]) == 1
        assert "individual3" in afal_client.session["individuals"].keys()
        assert response.url == "/apply-for-a-licence/individual_added"
        assert response.status_code == 302

    def test_unsuccessful_post(self, afal_client):
        request_object = RequestFactory().get("/")
        request_object.session = afal_client.session
        request_object.session["individuals"] = data.individuals
        request_object.session.save()
        response = afal_client.post(
            reverse("delete_individual"),
        )
        assert afal_client.session["individuals"] == data.individuals
        assert response.url == "/apply-for-a-licence/individual_added"
        assert response.status_code == 302