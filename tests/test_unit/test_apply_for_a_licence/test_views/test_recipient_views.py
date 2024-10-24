import uuid

from apply_for_a_licence.choices import TypeOfServicesChoices
from django.test import RequestFactory
from django.urls import reverse

from . import data


class TestAddRecipientView:
    def test_successful_post(self, al_client):
        assert al_client.session.get("recipients") is None
        recipient_uuid = str(uuid.uuid4())

        al_client.post(
            reverse("add_a_recipient", kwargs={"location": "in-uk", "recipient_uuid": recipient_uuid}),
            data={
                "name": "COOL BEANS LTD",
                "email": "thisismyemail@obviously.com",
                "address_line_1": "13 I live here",
                "address_line_2": "Flat bassment",
                "town_or_city": "Leeds",
                "postcode": "SW1A 1AA",
            },
            follow=True,
        )

        recipients = al_client.session.get("recipients")
        assert len(recipients) == 1

        assert recipients[recipient_uuid]["cleaned_data"]["name"] == "COOL BEANS LTD"
        assert (
            recipients[recipient_uuid]["cleaned_data"]["readable_address"]
            == "13 I live here,\n Flat bassment,\n Leeds,\n SW1A 1AA,\n United Kingdom"
        )

    def test_redirect_after_post(self, al_client):
        response = al_client.post(
            reverse("add_a_recipient", kwargs={"location": "in-uk", "recipient_uuid": uuid.uuid4()})
            + "?redirect_to_url=check_your_answers",
            data={
                "name": "COOL BEANS LTD",
                "email": "thisismyemail@obviously.com",
                "address_line_1": "13 I live here",
                "address_line_2": "Flat bassment",
                "town_or_city": "Leeds",
                "postcode": "SW1A 1AA",
            },
        )
        assert reverse("check_your_answers") in response.url

        response = al_client.post(
            reverse("add_a_recipient", kwargs={"location": "in-uk", "recipient_uuid": uuid.uuid4()})
            + "?redirect_to_url=check_your_answers&change=yes",
            data={
                "name": "COOL BEANS LTD",
                "email": "thisismyemail@obviously.com",
                "address_line_1": "13 I live here",
                "address_line_2": "Flat bassment",
                "town_or_city": "Leeds",
                "postcode": "SW1A 1AA",
            },
        )
        assert "provider-recipient-relationship" in response.url


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
        assert response.url == "/apply/add-recipient"
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
        assert response.url == "/apply/add-recipient"
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
        assert response.url == "/apply/add-recipient"
        assert response.status_code == 302


class TestRecipientAddedView:
    def test_success_url(self, al_client):
        response = al_client.post(
            reverse("recipient_added"),
            data={"do_you_want_to_add_another_recipient": "False"},
        )
        assert response.url == reverse("purpose_of_provision")

        response = al_client.post(reverse("recipient_added"), data={"do_you_want_to_add_another_recipient": "True"}, follow=True)
        assert response.wsgi_request.path == reverse("where_is_the_recipient_located", kwargs=response.resolver_match.kwargs)

        session = al_client.session
        session["type_of_service"] = {"type_of_service": TypeOfServicesChoices.professional_and_business.value}
        session.save()

        response = al_client.post(
            reverse("recipient_added"),
            data={"do_you_want_to_add_another_recipient": "False"},
        )
        assert response.url == reverse("licensing_grounds")


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
