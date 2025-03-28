from apply_for_a_licence import choices
from apply_for_a_licence.forms import forms_recipients as forms
from apply_for_a_licence.models import Licence, Organisation


class TestWhereIsTheRecipientLocatedForm:
    def test_required(self, request_object):
        form = forms.WhereIsTheRecipientLocatedForm(data={"where_is_the_address": None}, request=request_object)
        assert not form.is_valid()
        assert "where_is_the_address" in form.errors
        assert form.errors.as_data()["where_is_the_address"][0].code == "required"


class TestAddAUKRecipientForm:
    def test_required(self):
        form = forms.AddAUKRecipientForm(data={})
        assert not form.is_valid()
        assert "name" in form.errors
        assert "town_or_city" in form.errors
        assert "address_line_1" in form.errors
        assert "postcode" in form.errors
        assert form.errors.as_data()["name"][0].code == "required"
        assert form.errors.as_data()["town_or_city"][0].code == "required"
        assert form.errors.as_data()["address_line_1"][0].code == "required"
        assert form.errors.as_data()["postcode"][0].code == "required"

    def test_valid(self):
        form = forms.AddAUKRecipientForm(
            data={"name": "Business", "town_or_city": "London", "address_line_1": "40 Hollyhead", "postcode": "SW1A 1AA"},
        )
        assert form.is_valid()

    def test_incorrect_postcode_validation(self):

        form = forms.AddAUKRecipientForm(data={"postcode": "123"})
        assert not form.is_valid()
        assert "postcode" in form.errors
        assert form.errors.as_data()["postcode"][0].code == "invalid"


class TestAddNonUKRecipientForm:
    def test_required(self):
        form = forms.AddANonUKRecipientForm(data={})
        assert not form.is_valid()
        assert "name" in form.errors
        assert "country" in form.errors
        assert form.errors.as_data()["name"][0].code == "required"
        assert form.errors.as_data()["country"][0].code == "required"

    def test_valid(self):
        form = forms.AddANonUKRecipientForm(
            data={
                "name": "Business",
                "country": "BE",
                "town_or_city": "Leuven",
                "address_line_1": "Sesteenweg",
            },
        )
        assert form.is_valid()


class TestRecipientAddedForm:
    def test_required(self, post_request_object):
        form = forms.RecipientAddedForm(data={"do_you_want_to_add_another_recipient": None}, request=post_request_object)
        assert not form.is_valid()
        assert "do_you_want_to_add_another_recipient" in form.errors
        assert form.errors.as_data()["do_you_want_to_add_another_recipient"][0].code == "required"

    def test_never_bound_on_get(self, request_object):
        form = forms.RecipientAddedForm(request=request_object, data={"do_you_want_to_add_another_recipient": "True"})
        assert not form.is_bound

    def test_incomplete_recipient_raises_error(self, post_request_object, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=choices.WhoDoYouWantTheLicenceToCoverChoices.business.value
        )
        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        Organisation.objects.create(
            licence=licence,
            business_registered_on_companies_house=choices.YesNoDoNotKnowChoices.yes,
            type_of_relationship=choices.TypeOfRelationshipChoices.recipient.value,
            status="draft",
        )

        form = forms.RecipientAddedForm(
            data={"do_you_want_to_add_another_recipient": True}, request=post_request_object, licence_object=licence
        )
        assert form.errors.as_data()["__all__"][0].code == "incomplete_recipient"
        assert form.errors["__all__"][0] == (
            "You cannot add another recipient until Recipient 1 details are "
            "completed. Select 'change' and complete the details"
        )

        form = forms.RecipientAddedForm(
            data={"do_you_want_to_add_another_recipient": False}, request=post_request_object, licence_object=licence
        )
        assert form.errors.as_data()["__all__"][0].code == "incomplete_recipient"
        assert form.errors["__all__"][0] == (
            "Recipient 1 details have not yet been completed. " "Select 'change' and complete the details"
        )

        form = forms.RecipientAddedForm(data={}, request=post_request_object, licence_object=licence)
        assert form.errors.as_data()["__all__"][0].code == "incomplete_recipient"
        assert form.errors["__all__"][0] == (
            "Recipient 1 details have not yet been completed. " "Select 'change' and complete the details"
        )

    def test_incomplete_recipients_raises_error(self, post_request_object, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=choices.WhoDoYouWantTheLicenceToCoverChoices.business.value
        )
        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        Organisation.objects.create(
            licence=licence,
            business_registered_on_companies_house=choices.YesNoDoNotKnowChoices.yes,
            type_of_relationship=choices.TypeOfRelationshipChoices.recipient.value,
            status="complete",
        )

        Organisation.objects.create(
            licence=licence,
            business_registered_on_companies_house=choices.YesNoDoNotKnowChoices.yes,
            type_of_relationship=choices.TypeOfRelationshipChoices.recipient.value,
            status="draft",
        )

        form = forms.RecipientAddedForm(
            data={"do_you_want_to_add_another_recipient": True}, request=post_request_object, licence_object=licence
        )
        assert form.errors.as_data()["__all__"][0].code == "incomplete_recipient"
        assert form.errors["__all__"][0] == (
            "You cannot add another recipient until Recipient 2 details are either "
            "completed or the recipient is removed. Select 'change' and complete "
            "the details, or select 'Remove' to remove Recipient 2"
        )

        form = forms.RecipientAddedForm(
            data={"do_you_want_to_add_another_recipient": False}, request=post_request_object, licence_object=licence
        )
        assert form.errors.as_data()["__all__"][0].code == "incomplete_recipient"
        assert form.errors["__all__"][0] == (
            "Recipient 2 details have not yet been completed. Select 'change' and "
            "complete the details, or select 'Remove' to remove Recipient 2"
        )

        form = forms.RecipientAddedForm(data={}, request=post_request_object, licence_object=licence)
        assert form.errors.as_data()["__all__"][0].code == "incomplete_recipient"
        assert form.errors["__all__"][0] == (
            "Recipient 2 details have not yet been completed. Select 'change' and "
            "complete the details, or select 'Remove' to remove Recipient 2"
        )


class TestRelationshipProviderRecipientForm:
    def test_required(self, request_object):
        form = forms.RelationshipProviderRecipientForm(data={"relationship_provider": None}, request=request_object)
        assert not form.is_valid()
        assert "relationship_provider" in form.errors
        assert form.errors.as_data()["relationship_provider"][0].code == "required"
