import uuid

from apply_for_a_licence.choices import TypeOfServicesChoices
from django.test import RequestFactory
from django.urls import reverse

from . import data


class TestAddRecipientView:
    def test_successful_post(self, authenticated_al_client):
        assert authenticated_al_client.session.get("recipients") is None
        recipient_uuid = str(uuid.uuid4())

        authenticated_al_client.post(
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

        recipients = authenticated_al_client.session.get("recipients")
        assert len(recipients) == 1

        assert recipients[recipient_uuid]["cleaned_data"]["name"] == "COOL BEANS LTD"
        assert (
            recipients[recipient_uuid]["cleaned_data"]["readable_address"]
            == "13 I live here,\n Flat bassment,\n Leeds,\n SW1A 1AA,\n United Kingdom"
        )

    def test_redirect_after_post(self, authenticated_al_client):
        response = authenticated_al_client.post(
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

        response = authenticated_al_client.post(
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

    def test_get_form_new_recipient(self, authenticated_al_client):
        response = authenticated_al_client.get(
            reverse("add_a_recipient", kwargs={"location": "in-uk", "recipient_uuid": uuid.uuid4()})
        )
        assert response.context["form"].is_bound is False
        assert response.status_code == 200

    def test_get_form_is_not_bound_different_location(self, authenticated_al_client):
        recipient_uuid = uuid.uuid4()
        session = authenticated_al_client.session
        session["recipient_locations"] = {
            str(recipient_uuid): {
                "location": "in-uk",
                "changed": True,
            }
        }
        session.save()

        response = authenticated_al_client.get(
            reverse("add_a_recipient", kwargs={"location": "outside-uk", "recipient_uuid": recipient_uuid}) + "?change=yes"
        )
        assert response.context["form"].is_bound is False
        assert response.status_code == 200
        assert not session.get("recipients", {}).get(str(recipient_uuid), False)

    def test_get_form_is_bound_same_location(self, authenticated_al_client):
        recipient_uuid = uuid.uuid4()
        session = authenticated_al_client.session
        session["recipients"] = {
            str(recipient_uuid): {
                "cleaned_data": {
                    "url_location": "in-uk",
                },
                "dirty_data": {"address_line_1": "test address"},
            }
        }
        session.save()

        response = authenticated_al_client.get(
            reverse("add_a_recipient", kwargs={"location": "in-uk", "recipient_uuid": recipient_uuid}) + "?change=yes"
        )
        assert response.context["form"].is_bound

        response = authenticated_al_client.get(
            reverse("add_a_recipient", kwargs={"location": "outside-uk", "recipient_uuid": recipient_uuid}) + "?change=yes"
        )
        assert not response.context["form"].is_bound
        assert response.status_code == 200

    def test_post_form_complete_change(self, authenticated_al_client):
        recipient_uuid = uuid.uuid4()
        session = authenticated_al_client.session
        session["recipients"] = {
            str(recipient_uuid): {
                "cleaned_data": {
                    "url_location": "in-uk",
                },
                "dirty_data": {"address_line_1": "test address"},
            }
        }
        session.save()

        response = authenticated_al_client.post(
            reverse("add_a_recipient", kwargs={"location": "in-uk", "recipient_uuid": recipient_uuid})
            + "?redirect_to_url=check_your_answers&change=yes",
            data={
                "name": "COOL BEANS LTD",
                "email": "thisismyemail@obviously.com",
                "address_line_1": "13 I live here",
                "address_line_2": "Flat basement",
                "town_or_city": "Leeds",
                "postcode": "SW1A 1AA",
            },
        )

        assert response.status_code == 302
        assert authenticated_al_client.session["recipients"][str(recipient_uuid)]["cleaned_data"]["name"] == "COOL BEANS LTD"


class TestDeleteRecipientView:
    def test_successful_post(self, authenticated_al_client):
        request = RequestFactory().post("/")
        request.session = authenticated_al_client.session
        request.session["recipients"] = data.recipients
        recipient_id = "recipient1"
        request.session.save()
        response = authenticated_al_client.post(
            reverse("delete_recipient"),
            data={"recipient_uuid": recipient_id},
        )
        assert "recipient1" not in authenticated_al_client.session["recipients"].keys()
        assert authenticated_al_client.session["recipients"] != data.recipients
        assert response.url == "/apply/add-recipient"
        assert response.status_code == 302

    def test_cannot_delete_all_recipients_post(self, authenticated_al_client):
        request = RequestFactory().post("/")
        request.session = authenticated_al_client.session
        request.session["recipients"] = data.recipients
        request.session.save()
        response = authenticated_al_client.post(
            reverse("delete_recipient"),
            data={"recipient_uuid": "recipient1"},
        )
        response = authenticated_al_client.post(
            reverse("delete_recipient"),
            data={"recipient_uuid": "recipient2"},
        )
        response = authenticated_al_client.post(
            reverse("delete_recipient"),
            data={"recipient_uuid": "recipient3"},
        )
        # does not delete last recipient
        assert len(authenticated_al_client.session["recipients"]) == 1
        assert "recipient3" in authenticated_al_client.session["recipients"].keys()
        assert response.url == "/apply/add-recipient"
        assert response.status_code == 302

    def test_unsuccessful_post(self, authenticated_al_client):
        request_object = RequestFactory().get("/")
        request_object.session = authenticated_al_client.session
        request_object.session["recipients"] = data.recipients
        request_object.session.save()
        response = authenticated_al_client.post(
            reverse("delete_recipient"),
        )
        assert authenticated_al_client.session["recipients"] == data.recipients
        assert response.url == "/apply/add-recipient"
        assert response.status_code == 302


class TestRecipientAddedView:
    def test_success_url(self, authenticated_al_client):
        response = authenticated_al_client.post(
            reverse("recipient_added"),
            data={"do_you_want_to_add_another_recipient": "False"},
        )
        assert response.url == reverse("purpose_of_provision")

        response = authenticated_al_client.post(
            reverse("recipient_added"), data={"do_you_want_to_add_another_recipient": "True"}, follow=True
        )
        assert response.wsgi_request.path == reverse("where_is_the_recipient_located", kwargs=response.resolver_match.kwargs)

        session = authenticated_al_client.session
        session["type_of_service"] = {"type_of_service": TypeOfServicesChoices.professional_and_business.value}
        session.save()

        response = authenticated_al_client.post(
            reverse("recipient_added"),
            data={"do_you_want_to_add_another_recipient": "False"},
        )
        assert response.url == reverse("licensing_grounds")


class TestRelationshipProviderRecipientView:
    def test_successful_post(self, authenticated_al_client):
        session = authenticated_al_client.session
        session["recipients"] = data.recipients
        session.save()

        authenticated_al_client.post(
            reverse("relationship_provider_recipient", kwargs={"recipient_uuid": "recipient1"}),
            data={"relationship": "this is a relationship"},
        )

        assert authenticated_al_client.session["recipients"]["recipient1"]["relationship"] == "this is a relationship"
        assert "relationship" not in authenticated_al_client.session["recipients"]["recipient2"].keys()

    def test_get(self, authenticated_al_client):
        recipient1 = data.recipients["recipient1"].copy()
        recipient1["relationship"] = "this is a relationship"
        session = authenticated_al_client.session
        session["recipients"] = {"recipient1": recipient1}
        session.save()

        response = authenticated_al_client.get(
            reverse("relationship_provider_recipient", kwargs={"recipient_uuid": "recipient1"}),
        )
        assert response.context["form"].data["relationship"] == "this is a relationship"

    def test_get_not_bound(self, authenticated_al_client):
        response = authenticated_al_client.get(
            reverse("relationship_provider_recipient", kwargs={"recipient_uuid": "recipientNA"}),
        )
        assert not response.context["form"].is_bound


class TestWhereIsTheRecipientLocatedView:
    def test_form_valid(self, authenticated_al_client):
        # first recipient
        first_recipient_uuid = uuid.uuid4()
        response = authenticated_al_client.post(
            reverse("where_is_the_recipient_located", kwargs={"recipient_uuid": first_recipient_uuid}),
            data={"where_is_the_address": "in-uk"},
        )

        assert response.status_code == 302
        assert response.url == reverse("add_a_recipient", kwargs={"recipient_uuid": first_recipient_uuid, "location": "in-uk"})
        assert authenticated_al_client.session["recipient_locations"][str(first_recipient_uuid)]["location"] == "in-uk"
        assert authenticated_al_client.session["recipient_locations"][str(first_recipient_uuid)]["changed"] is False

        # new recipient
        new_recipient_uuid = uuid.uuid4()
        response = authenticated_al_client.post(
            reverse("where_is_the_recipient_located", kwargs={"recipient_uuid": new_recipient_uuid}),
            data={"where_is_the_address": "outside-uk"},
        )

        assert response.status_code == 302
        assert response.url == reverse("add_a_recipient", kwargs={"recipient_uuid": new_recipient_uuid, "location": "outside-uk"})
        assert authenticated_al_client.session["recipient_locations"][str(new_recipient_uuid)]["location"] == "outside-uk"
        assert authenticated_al_client.session["recipient_locations"][str(new_recipient_uuid)]["changed"] is False

        # change first recipients location
        response = authenticated_al_client.post(
            reverse("where_is_the_recipient_located", kwargs={"recipient_uuid": first_recipient_uuid}) + "?change=true",
            data={"where_is_the_address": "outside-uk"},
        )

        assert response.status_code == 302
        assert (
            response.url
            == reverse("add_a_recipient", kwargs={"recipient_uuid": first_recipient_uuid, "location": "outside-uk"})
            + "?change=true"
        )
        assert authenticated_al_client.session["recipient_locations"][str(first_recipient_uuid)]["changed"] is True
