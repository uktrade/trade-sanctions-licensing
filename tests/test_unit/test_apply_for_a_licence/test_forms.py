from datetime import timedelta
from unittest.mock import patch

import pytest
from apply_for_a_licence import choices, forms
from apply_for_a_licence.models import Regime, UserEmailVerification
from django import forms as django_forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory

from tests.factories import RegimeFactory


class TestStartForm:
    def test_required(self):
        form = forms.StartForm(data={"who_do_you_want_the_licence_to_cover": None})
        assert not form.is_valid()
        assert "who_do_you_want_the_licence_to_cover" in form.errors
        assert form.errors.as_data()["who_do_you_want_the_licence_to_cover"][0].code == "required"

    def test_widget(self):
        form = forms.StartForm()
        assert isinstance(form.fields["who_do_you_want_the_licence_to_cover"].widget, django_forms.RadioSelect)


class TestThirdPartyForm:
    def test_required(self):
        form = forms.ThirdPartyForm(data={"are_you_applying_on_behalf_of_someone_else": None})
        assert not form.is_valid()
        assert "are_you_applying_on_behalf_of_someone_else" in form.errors
        assert form.errors.as_data()["are_you_applying_on_behalf_of_someone_else"][0].code == "required"


class TestEmailForm:
    def test_required(self):
        form = forms.WhatIsYourEmailForm(data={"email": None})
        assert not form.is_valid()
        assert "email" in form.errors
        assert form.errors.as_data()["email"][0].code == "required"

    def test_invalid(self):
        form = forms.WhatIsYourEmailForm(data={"email": "invalid"})
        assert not form.is_valid()
        assert "email" in form.errors
        assert form.errors.as_data()["email"][0].code == "invalid"


class TestEmailVerifyForm:
    verify_code = "123456"

    @pytest.fixture(autouse=True)
    def user_email_verification_object(self, afal_client):
        self.obj = UserEmailVerification.objects.create(
            user_session=afal_client.session._get_session_from_db(),
            email_verification_code=self.verify_code,
        )
        user_request_object = RequestFactory()
        user_request_object.session = afal_client.session._get_session_from_db()
        self.request_object = user_request_object

    def test_email_verify_form_correct(self, afal_client):
        form = forms.EmailVerifyForm(data={"email_verification_code": self.verify_code}, request=self.request_object)
        assert form.is_valid()

    def test_email_verify_form_incorrect_code(self, afal_client):
        form = forms.EmailVerifyForm(data={"email_verification_code": "1"}, request=self.request_object)
        assert not form.is_valid()
        assert "email_verification_code" in form.errors

    def test_email_verify_form_expired_code_2_hours(self, afal_client):
        self.obj.date_created = self.obj.date_created - timedelta(days=1)
        self.obj.save()
        form = forms.EmailVerifyForm(data={"email_verification_code": self.verify_code}, request=self.request_object)
        assert not form.is_valid()
        assert form.has_error("email_verification_code", "invalid")

    def test_email_verify_form_expired_code_1_hour(self, afal_client):
        self.obj.date_created = self.obj.date_created - timedelta(minutes=61)
        self.obj.save()
        form = forms.EmailVerifyForm(data={"email_verification_code": self.verify_code}, request=self.request_object)
        assert not form.is_valid()
        assert form.has_error("email_verification_code", "expired")


class TestYourDetailsForm:
    def test_required(self):
        form = forms.YourDetailsForm(data={"full_name": None})
        assert not form.is_valid()
        assert "full_name" in form.errors
        assert form.errors.as_data()["full_name"][0].code == "required"


class TestIsTheBusinessRegisteredWithCompaniesHouseForm:
    def test_business_registered_on_companies_house_required(self):
        form = forms.IsTheBusinessRegisteredWithCompaniesHouseForm(data={"business_registered_on_companies_house": None})
        assert not form.is_valid()
        assert "business_registered_on_companies_house" in form.errors
        assert form.errors.as_data()["business_registered_on_companies_house"][0].code == "required"

    def test_optional_choice_removed(self):
        form = forms.IsTheBusinessRegisteredWithCompaniesHouseForm()
        assert len(form.fields["business_registered_on_companies_house"].choices) == len(choices.YesNoDoNotKnowChoices.choices)


class TestExistingLicenceForm:
    def test_required(self, request_object):
        form = forms.ExistingLicencesForm(data={"held_existing_licence": None}, request=request_object)
        assert not form.is_valid()
        assert "held_existing_licence" in form.errors
        assert form.errors.as_data()["held_existing_licence"][0].code == "required"


class TestDoYouKnowTheRegisteredCompanyNumberForm:
    def test_do_you_know_the_registered_company_number_required(self, request_object):
        form = forms.DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": None}, request=request_object
        )
        assert not form.is_valid()
        assert "do_you_know_the_registered_company_number" in form.errors
        assert form.errors.as_data()["do_you_know_the_registered_company_number"][0].code == "required"

    def test_registered_company_number_required(self, request_object):
        form = forms.DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": None}, request=request_object
        )
        assert not form.is_valid()
        assert "registered_company_number" in form.errors
        assert form.errors.as_data()["registered_company_number"][0].code == "required"

    def test_registered_company_number_not_required(self, request_object):
        form = forms.DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "no", "registered_company_number": None}, request=request_object
        )
        assert form.is_valid()

    @patch("apply_for_a_licence.forms.get_details_from_companies_house")
    @patch("apply_for_a_licence.forms.get_formatted_address")
    def test_clean(self, mocked_get_formatted_address, mocked_get_details_from_companies_house, request_object):
        mocked_get_details_from_companies_house.return_value = {
            "company_number": "12345678",
            "company_name": "Test Company",
            "registered_office_address": "",
        }
        mocked_get_formatted_address.return_value = "12 road, London"

        form = forms.DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
            request=request_object,
        )
        form.is_valid()
        cleaned_data = form.clean()
        assert cleaned_data["registered_company_name"] == "Test Company"
        assert cleaned_data["registered_office_address"] == "12 road, London"
        assert cleaned_data["registered_company_number"] == "12345678"

    def test_form_is_unbound(self, request_object):
        form = forms.DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
            request=request_object,
        )
        assert form.is_bound

        request_object.GET = {"change": "yes"}
        form = forms.DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
            request=request_object,
        )
        assert not form.is_bound


class TestManualCompaniesHouseInputForm:
    def test_required(self, request_object):
        form = forms.ManualCompaniesHouseInputForm(data={"manual_companies_house_input": None}, request=request_object)
        assert not form.is_valid()
        assert "manual_companies_house_input" in form.errors
        assert form.errors.as_data()["manual_companies_house_input"][0].code == "required"


class TestWhereIsTheBusinessLocatedForm:
    def test_required(self, request_object):
        form = forms.WhereIsTheBusinessLocatedForm(data={"where_is_the_address": None}, request=request_object)
        assert not form.is_valid()
        assert "where_is_the_address" in form.errors
        assert form.errors.as_data()["where_is_the_address"][0].code == "required"


class TestAddABusinessForm:
    def test_uk_required(self):
        form = forms.AddABusinessForm(data={}, is_uk_address=True)
        assert not form.is_valid()
        assert "name" in form.errors
        assert "postcode" in form.errors
        assert form.errors.as_data()["name"][0].code == "required"
        assert form.errors.as_data()["postcode"][0].code == "required"

    def test_uk_valid(self):
        form = forms.AddABusinessForm(
            data={"name": "Business", "town_or_city": "London", "address_line_1": "40 Hollyhead", "postcode": "SW1A 1AA"},
            is_uk_address=True,
        )
        assert form.is_valid()

    def test_non_uk_required(self):
        form = forms.AddABusinessForm(data={}, is_uk_address=False)
        assert not form.is_valid()
        assert "name" in form.errors
        assert "country" in form.errors
        assert form.errors.as_data()["name"][0].code == "required"
        assert form.errors.as_data()["country"][0].code == "required"

    def test_non_uk_valid(self):
        form = forms.AddABusinessForm(
            data={
                "name": "Business",
                "country": "BE",
            },
            is_uk_address=False,
        )
        assert form.is_valid()

    def test_incorrect_postcode_validation(self):

        form = forms.AddABusinessForm(data={"postcode": "123"}, is_uk_address=True)
        assert not form.is_valid()
        assert "postcode" in form.errors
        assert form.errors.as_data()["postcode"][0].code == "invalid"


class TestBusinessAddedForm:
    def test_required(self, request_object):
        form = forms.BusinessAddedForm(data={"do_you_want_to_add_another_business": None}, request=request_object)
        assert not form.is_valid()
        assert "do_you_want_to_add_another_business" in form.errors
        assert form.errors.as_data()["do_you_want_to_add_another_business"][0].code == "required"


class TestAddAnIndividualForm:
    def test_required(self, request_object):
        form = forms.AddAnIndividualForm(
            data={"first_name": None, "last_name": None, "nationality_and_location": None}, request=request_object
        )
        assert not form.is_valid()
        assert "first_name" in form.errors
        assert "last_name" in form.errors
        assert "nationality_and_location" in form.errors
        assert form.errors.as_data()["first_name"][0].code == "required"
        assert form.errors.as_data()["last_name"][0].code == "required"
        assert form.errors.as_data()["nationality_and_location"][0].code == "required"


class TestIndividualAddedForm:
    def test_required(self, request_object):
        form = forms.IndividualAddedForm(data={"do_you_want_to_add_another_individual": None}, request=request_object)
        assert not form.is_valid()
        assert "do_you_want_to_add_another_individual" in form.errors
        assert form.errors.as_data()["do_you_want_to_add_another_individual"][0].code == "required"


class TestBusinessEmployingIndividualForm:
    def test_required(self, request_object):
        form = forms.BusinessEmployingIndividualForm(data={}, request=request_object)
        assert not form.is_valid()
        assert "name" in form.errors
        assert "country" in form.errors
        assert form.errors.as_data()["name"][0].code == "required"
        assert form.errors.as_data()["country"][0].code == "required"


class TestAddYourselfForm:
    def test_required(self, request_object):
        form = forms.AddYourselfForm(
            data={"first_name": None, "last_name": None, "nationality_and_location": None}, request=request_object
        )
        assert not form.is_valid()
        assert "first_name" in form.errors
        assert "last_name" in form.errors
        assert "nationality_and_location" in form.errors
        assert form.errors.as_data()["first_name"][0].code == "required"
        assert form.errors.as_data()["last_name"][0].code == "required"
        assert form.errors.as_data()["nationality_and_location"][0].code == "required"


class TestAddYourselfAddressForm:
    def test_uk_required(self):
        form = forms.AddYourselfAddressForm(data={}, is_uk_address=True)
        assert not form.is_valid()
        assert "town_or_city" in form.errors
        assert "address_line_1" in form.errors
        assert "postcode" in form.errors
        assert form.errors.as_data()["town_or_city"][0].code == "required"
        assert form.errors.as_data()["address_line_1"][0].code == "required"
        assert form.errors.as_data()["postcode"][0].code == "required"

    def test_uk_valid(self):
        form = forms.AddYourselfAddressForm(
            data={"town_or_city": "London", "address_line_1": "40 Hollyhead", "postcode": "SW1A 1AA"}, is_uk_address=True
        )
        assert form.is_valid()

    def test_non_uk_required(self):
        form = forms.AddYourselfAddressForm(data={"country": None}, is_uk_address=False)
        assert not form.is_valid()
        assert "town_or_city" in form.errors
        assert "address_line_1" in form.errors
        assert "country" in form.errors
        assert form.errors.as_data()["country"][0].code == "required"
        assert form.errors.as_data()["town_or_city"][0].code == "required"
        assert form.errors.as_data()["address_line_1"][0].code == "required"

    def test_non_uk_valid(self):
        form = forms.AddYourselfAddressForm(
            data={"country": "BE", "town_or_city": "Brussels", "address_line_1": "Rue Neuve"}, is_uk_address=False
        )
        assert form.is_valid()

    def test_incorrect_postcode_validation(self):

        form = forms.AddYourselfAddressForm(data={"postcode": "123"}, is_uk_address=True)
        assert not form.is_valid()
        assert "postcode" in form.errors
        assert form.errors.as_data()["postcode"][0].code == "invalid"


class TestTypeOfServiceForm:
    def test_required(self, request_object):
        form = forms.TypeOfServiceForm(data={"type_of_service": None}, request=request_object)
        assert not form.is_valid()
        assert "type_of_service" in form.errors
        assert form.errors.as_data()["type_of_service"][0].code == "required"


@pytest.mark.django_db
class TestWhichSanctionsRegimeForm:
    def test_required(self, request_object):
        form = forms.WhichSanctionsRegimeForm(data={"which_sanctions_regime": None}, request=request_object)
        assert not form.is_valid()
        assert "which_sanctions_regime" in form.errors
        assert form.errors.as_data()["which_sanctions_regime"][0].code == "required"

    def test_choices_creation(self, request_object):
        RegimeFactory.create_batch(5)
        form = forms.WhichSanctionsRegimeForm(request=request_object)
        assert len(form.fields["which_sanctions_regime"].choices) == 5
        flat_choices = [choice[0] for choice in form.fields["which_sanctions_regime"].choices]
        for regime in Regime.objects.all():
            assert regime.full_name in flat_choices


class TestProfessionalOrBusinessServicesForm:
    def test_required(self, request_object):
        form = forms.ProfessionalOrBusinessServicesForm(data={"professional_or_business_service": None}, request=request_object)
        assert not form.is_valid()
        assert "professional_or_business_service" in form.errors
        assert form.errors.as_data()["professional_or_business_service"][0].code == "required"


class TestServiceActivitiesForm:
    def test_required(self, request_object):
        form = forms.ServiceActivitiesForm(data={"service_activities": None}, request=request_object)
        assert not form.is_valid()
        assert "service_activities" in form.errors
        assert form.errors.as_data()["service_activities"][0].code == "required"


class TestWhereIsTheRecipientLocatedForm:
    def test_required(self, request_object):
        form = forms.WhereIsTheRecipientLocatedForm(data={"where_is_the_address": None}, request=request_object)
        assert not form.is_valid()
        assert "where_is_the_address" in form.errors
        assert form.errors.as_data()["where_is_the_address"][0].code == "required"


class TestAddARecipientForm:
    def test_uk_required(self):
        form = forms.AddARecipientForm(data={}, is_uk_address=True)
        assert not form.is_valid()
        assert "name" in form.errors
        assert "town_or_city" in form.errors
        assert "address_line_1" in form.errors
        assert "postcode" in form.errors
        assert form.errors.as_data()["name"][0].code == "required"
        assert form.errors.as_data()["town_or_city"][0].code == "required"
        assert form.errors.as_data()["address_line_1"][0].code == "required"
        assert form.errors.as_data()["postcode"][0].code == "required"

    def test_uk_valid(self):
        form = forms.AddARecipientForm(
            data={"name": "Business", "town_or_city": "London", "address_line_1": "40 Hollyhead", "postcode": "SW1A 1AA"},
            is_uk_address=True,
        )
        assert form.is_valid()

    def test_non_uk_required(self):
        form = forms.AddARecipientForm(data={}, is_uk_address=False)
        assert not form.is_valid()
        assert "name" in form.errors
        assert "country" in form.errors
        assert form.errors.as_data()["name"][0].code == "required"
        assert form.errors.as_data()["country"][0].code == "required"

    def test_non_uk_valid(self):
        form = forms.AddARecipientForm(
            data={
                "name": "Business",
                "country": "BE",
                "town_or_city": "Leuven",
                "address_line_1": "Sesteenweg",
            },
            is_uk_address=False,
        )
        assert form.is_valid()

    def test_incorrect_postcode_validation(self):

        form = forms.AddARecipientForm(data={"postcode": "123"}, is_uk_address=True)
        assert not form.is_valid()
        assert "postcode" in form.errors
        assert form.errors.as_data()["postcode"][0].code == "invalid"


class TestRecipientAddedForm:
    def test_required(self, request_object):
        form = forms.RecipientAddedForm(data={"do_you_want_to_add_another_recipient": None}, request=request_object)
        assert not form.is_valid()
        assert "do_you_want_to_add_another_recipient" in form.errors
        assert form.errors.as_data()["do_you_want_to_add_another_recipient"][0].code == "required"


class TestRelationshipProviderRecipientForm:
    def test_required(self, request_object):
        form = forms.RelationshipProviderRecipientForm(data={"relationship": None}, request=request_object)
        assert not form.is_valid()
        assert "relationship" in form.errors
        assert form.errors.as_data()["relationship"][0].code == "required"


class TestLicensingGroundsForm:
    def test_required(self, request_object):
        form = forms.LicensingGroundsForm(data={"licensing_grounds": None}, request=request_object)
        assert not form.is_valid()
        assert "licensing_grounds" in form.errors
        assert form.errors.as_data()["licensing_grounds"][0].code == "required"


class TestPurposeOfProvisionForm:
    def test_required(self, request_object):
        form = forms.PurposeOfProvisionForm(data={"purpose_of_provision": None}, request=request_object)
        assert not form.is_valid()
        assert "purpose_of_provision" in form.errors
        assert form.errors.as_data()["purpose_of_provision"][0].code == "required"


class TestUploadDocumentsForm:
    class MockAllSessionFiles:
        def __init__(self, length: int = 0):
            self.length = length
            super().__init__()

        def __len__(self):
            return self.length

    def test_valid(self, request_object):
        good_file = SimpleUploadedFile("good.pdf", b"%PDF-test_pdf")

        form = forms.UploadDocumentsForm(
            files={
                "document": [
                    good_file,
                ]
            },
            request=request_object,
        )
        assert form.is_valid()

    def test_invalid_mimetype(self, request_object):
        bad_file = SimpleUploadedFile("bad.gif", b"GIF8")

        form = forms.UploadDocumentsForm(
            files={
                "document": [
                    bad_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].code == "invalid_file_type"

    def test_invalid_extension(self, request_object):
        bad_file = SimpleUploadedFile("bad.gif", b"%PDF-test_pdf")

        form = forms.UploadDocumentsForm(
            files={
                "document": [
                    bad_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].code == "invalid_file_type"

    def test_too_large(self, request_object):
        large_file = SimpleUploadedFile("large.pdf", b"%PDF-test_pdf")
        large_file.size = 9999999999

        form = forms.UploadDocumentsForm(
            files={
                "document": [
                    large_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].code == "too_large"

    @patch("apply_for_a_licence.forms.get_all_session_files", return_value=MockAllSessionFiles(length=10))
    def test_too_many_uploaded(self, mocked_get_all_session_files, request_object):
        good_file = SimpleUploadedFile("good.pdf", b"%PDF-test_pdf")

        form = forms.UploadDocumentsForm(
            files={
                "document": [
                    good_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].code == "too_many"

    def test_invalid_extension_file_name_escaped(self, request_object):
        bad_file = SimpleUploadedFile("<img src=xonerror=alert(document.domain)>gif.gif", b"GIF8")

        form = forms.UploadDocumentsForm(
            files={
                "document": [
                    bad_file,
                ]
            },
            request=request_object,
        )
        assert not form.is_valid()
        assert "document" in form.errors
        assert form.errors.as_data()["document"][0].message == (
            "&lt;img src=xonerror=alert(document.domain)&gt;gif." "gif cannot be uploaded, it is not a valid file type"
        )
