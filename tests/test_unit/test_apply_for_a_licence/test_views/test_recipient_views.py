from apply_for_a_licence.choices import TypeOfServicesChoices
from apply_for_a_licence.models import Organisation
from django.urls import reverse

from tests.factories import OrganisationFactory


class TestAddRecipientView:
    def test_successful_post(self, authenticated_al_client_with_licence, licence_application):
        assert authenticated_al_client_with_licence.session.get("recipients") is None

        organisation = OrganisationFactory(
            licence=licence_application,
            where_is_the_address="in-uk",
        )

        authenticated_al_client_with_licence.post(
            reverse("add_a_recipient", kwargs={"location": "in-uk", "recipient_id": organisation.id}),
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
        organisation.refresh_from_db()
        assert Organisation.objects.filter(licence=licence_application).count() == 1
        assert organisation.name == "COOL BEANS LTD"
        assert organisation.email == "thisismyemail@obviously.com"
        assert organisation.address_line_1 == "13 I live here"
        assert organisation.address_line_2 == "Flat bassment"
        assert organisation.town_or_city == "Leeds"
        assert organisation.postcode == "SW1A 1AA"

    def test_redirect_after_post(self, authenticated_al_client_with_licence, licence_application):
        organisation = OrganisationFactory(
            licence=licence_application,
            where_is_the_address="in-uk",
        )

        response = authenticated_al_client_with_licence.post(
            reverse("add_a_recipient", kwargs={"location": "in-uk", "recipient_id": organisation.id}),
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

        response = authenticated_al_client_with_licence.post(
            reverse("add_a_recipient", kwargs={"location": "in-uk", "recipient_id": organisation.id}),
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

    def test_get_form_new_recipient(self, authenticated_al_client, organisation):
        response = authenticated_al_client.get(
            reverse("add_a_recipient", kwargs={"location": "in-uk", "recipient_id": organisation.id})
        )
        assert response.context["form"].is_bound is False
        assert response.status_code == 200

    def test_get_form_is_not_bound_different_location(self, authenticated_al_client, organisation):
        organisation.where_is_the_address = "in-uk"
        organisation.address_line_1 = "13 I live here"
        organisation.save()

        response = authenticated_al_client.post(
            reverse(
                "where_is_the_recipient_located",
                kwargs={"recipient_id": organisation.id},
            )
            + "?change=yes",
            data={"where_is_the_address": "outside-uk"},
        )
        assert response.status_code == 302
        assert (
            response.url
            == reverse("add_a_recipient", kwargs={"location": "outside-uk", "recipient_id": organisation.id}) + "?change=yes"
        )
        organisation.refresh_from_db()
        assert not organisation.address_line_1

    def test_get_form_is_bound_same_location(self, authenticated_al_client, organisation):
        organisation.where_is_the_address = "in-uk"
        organisation.address_line_1 = "13 I live here"
        organisation.save()

        response = authenticated_al_client.post(
            reverse(
                "where_is_the_recipient_located",
                kwargs={"recipient_id": organisation.id},
            )
            + "?change=yes",
            data={"where_is_the_address": "in-uk"},
        )
        assert response.status_code == 302
        assert (
            response.url
            == reverse("add_a_recipient", kwargs={"location": "in-uk", "recipient_id": organisation.pk}) + "?change=yes"
        )
        organisation.refresh_from_db()
        assert organisation.address_line_1 == "13 I live here"

    def test_post_form_complete_change(self, authenticated_al_client_with_licence, licence_application, organisation):
        organisation.where_is_the_address = "in-uk"
        organisation.save()

        response = authenticated_al_client_with_licence.post(
            reverse("add_a_recipient", kwargs={"location": "in-uk", "recipient_id": organisation.id})
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
        organisation.refresh_from_db()
        assert organisation.name == "COOL BEANS LTD"


class TestDeleteRecipientView:
    def test_successful_post(self, authenticated_al_client_with_licence, organisation):
        organisation.type_of_relationship = "recipient"
        organisation.save()

        response = authenticated_al_client_with_licence.post(
            reverse("delete_recipient", kwargs={"recipient_id": organisation.id}),
        )
        try:
            organisation.refresh_from_db()
            assert False
        except Organisation.DoesNotExist:
            pass
        assert response.url == "/apply/add-recipient"
        assert response.status_code == 302

    def test_cannot_delete_all_recipients_post(self, authenticated_al_client_with_licence, licence_application):
        recipients = OrganisationFactory.create_batch(4, licence=licence_application, type_of_relationship="recipient")

        # does not delete last recipient
        for recipient in recipients[:-1]:
            response = authenticated_al_client_with_licence.post(
                reverse("delete_recipient", kwargs={"recipient_id": recipient.id}),
            )
            try:
                recipient.refresh_from_db()
                assert False
            except Organisation.DoesNotExist:
                pass

        recipients[-1].refresh_from_db()
        assert response.url == "/apply/add-recipient"
        assert response.status_code == 302

    def test_unsuccessful_post(self, authenticated_al_client_with_licence, organisation):
        response = authenticated_al_client_with_licence.post(
            reverse("delete_recipient", kwargs={"recipient_id": 1111111}),
        )
        organisation.refresh_from_db()
        assert response.status_code == 404


class TestRecipientAddedView:
    def test_success_url(self, authenticated_al_client_with_licence, licence_application):
        licence_application.type_of_service = TypeOfServicesChoices.infrastructure_or_tourism_related.value
        licence_application.save()

        response = authenticated_al_client_with_licence.post(
            reverse("recipient_added"),
            data={"do_you_want_to_add_another_recipient": "False"},
        )
        assert response.url == reverse("tasklist")

        response = authenticated_al_client_with_licence.post(
            reverse("recipient_added"), data={"do_you_want_to_add_another_recipient": "True"}, follow=True
        )
        assert response.wsgi_request.path == reverse("where_is_the_recipient_located", kwargs=response.resolver_match.kwargs)


class TestRelationshipProviderRecipientView:
    def test_successful_post(self, authenticated_al_client_with_licence, recipient_organisation):
        authenticated_al_client_with_licence.post(
            reverse("relationship_provider_recipient", kwargs={"recipient_id": recipient_organisation.id}),
            data={"relationship_provider": "this is a relationship"},
        )
        recipient_organisation.refresh_from_db()
        assert recipient_organisation.relationship_provider == "this is a relationship"

    def test_get(self, authenticated_al_client_with_licence, recipient_organisation):
        recipient_organisation.relationship_provider = "this is a test"
        recipient_organisation.save()

        response = authenticated_al_client_with_licence.get(
            reverse("relationship_provider_recipient", kwargs={"recipient_id": recipient_organisation.id}),
        )
        assert response.context["form"].initial["relationship_provider"] == "this is a test"

    def test_get_not_bound(self, authenticated_al_client_with_licence):
        response = authenticated_al_client_with_licence.get(
            reverse("relationship_provider_recipient", kwargs={"recipient_id": 11111111}),
        )
        assert response.status_code == 404


class TestWhereIsTheRecipientLocatedView:
    def test_form_valid(self, authenticated_al_client_with_licence, recipient_organisation, licence_application):
        # first recipient
        recipient_organisation.where_is_the_address = "outside-uk"
        recipient_organisation.save()

        response = authenticated_al_client_with_licence.post(
            reverse("where_is_the_recipient_located", kwargs={"recipient_id": recipient_organisation.id}),
            data={"where_is_the_address": "in-uk"},
        )

        assert response.status_code == 302
        assert response.url == reverse("add_a_recipient", kwargs={"recipient_id": recipient_organisation.id, "location": "in-uk"})
        recipient_organisation.refresh_from_db()
        assert recipient_organisation.where_is_the_address == "in-uk"

        # change first recipients location
        response = authenticated_al_client_with_licence.post(
            reverse("where_is_the_recipient_located", kwargs={"recipient_id": recipient_organisation.id}) + "?change=true",
            data={"where_is_the_address": "outside-uk"},
        )

        assert response.status_code == 302
        assert (
            response.url
            == reverse("add_a_recipient", kwargs={"recipient_id": recipient_organisation.id, "location": "outside-uk"})
            + "?change=true"
        )
        recipient_organisation.refresh_from_db()
        assert recipient_organisation.where_is_the_address == "outside-uk"
