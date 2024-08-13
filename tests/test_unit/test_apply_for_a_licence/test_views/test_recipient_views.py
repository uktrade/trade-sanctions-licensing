from django.test import RequestFactory
from django.urls import reverse

from . import data


class TestDeleteRecipientView:
    def test_successful_post(self, al_client):
        request = RequestFactory().post("/")
        request.session = al_client.session
        request.session["recipients"] = data.recipients
        recipient_id = "recipient1"
        request.session.save()
        response = al_client.post(
            reverse("delete_recipient"),
            data={"recipient_uuid": recipient_id},
        )
        assert "recipient1" not in al_client.session["recipients"].keys()
        assert al_client.session["recipients"] != data.recipients
        assert response.url == "/apply-for-a-licence/recipient_added"
        assert response.status_code == 302

    def test_cannot_delete_all_recipients_post(self, al_client):
        request = RequestFactory().post("/")
        request.session = al_client.session
        request.session["recipients"] = data.recipients
        request.session.save()
        response = al_client.post(
            reverse("delete_recipient"),
            data={"recipient_uuid": "recipient1"},
        )
        response = al_client.post(
            reverse("delete_recipient"),
            data={"recipient_uuid": "recipient2"},
        )
        response = al_client.post(
            reverse("delete_recipient"),
            data={"recipient_uuid": "recipient3"},
        )
        # does not delete last recipient
        assert len(al_client.session["recipients"]) == 1
        assert "recipient3" in al_client.session["recipients"].keys()
        assert response.url == "/apply-for-a-licence/recipient_added"
        assert response.status_code == 302

    def test_unsuccessful_post(self, al_client):
        request_object = RequestFactory().get("/")
        request_object.session = al_client.session
        request_object.session["recipients"] = data.recipients
        request_object.session.save()
        response = al_client.post(
            reverse("delete_recipient"),
        )
        assert al_client.session["recipients"] == data.recipients
        assert response.url == "/apply-for-a-licence/recipient_added"
        assert response.status_code == 302


class TestRelationshipProviderRecipientView:
    def test_successful_post(self, al_client):
        session = al_client.session
        session["recipients"] = data.recipients
        session.save()

        al_client.post(
            reverse("relationship_provider_recipient", kwargs={"recipient_uuid": "recipient1"}),
            data={"relationship": "this is a relationship"},
        )

        assert al_client.session["recipients"]["recipient1"]["relationship"] == "this is a relationship"
        assert "relationship" not in al_client.session["recipients"]["recipient2"].keys()

    def test_get(self, al_client):
        recipient1 = data.recipients["recipient1"].copy()
        recipient1["relationship"] = "this is a relationship"
        session = al_client.session
        session["recipients"] = {"recipient1": recipient1}
        session.save()

        response = al_client.get(
            reverse("relationship_provider_recipient", kwargs={"recipient_uuid": "recipient1"}),
        )
        assert response.context["form"].data["relationship"] == "this is a relationship"

    def test_get_not_bound(self, al_client):
        response = al_client.get(
            reverse("relationship_provider_recipient", kwargs={"recipient_uuid": "recipientNA"}),
        )
        assert not response.context["form"].is_bound
