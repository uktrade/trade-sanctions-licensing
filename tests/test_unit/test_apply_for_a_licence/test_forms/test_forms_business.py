from unittest.mock import patch

from apply_for_a_licence import choices
from apply_for_a_licence.forms import forms_business as forms


class TestIsTheBusinessRegisteredWithCompaniesHouseForm:
    def test_business_registered_on_companies_house_required(self, request_object):
        form = forms.IsTheBusinessRegisteredWithCompaniesHouseForm(
            data={"business_registered_on_companies_house": None}, request=request_object
        )
        assert not form.is_valid()
        assert "business_registered_on_companies_house" in form.errors
        assert form.errors.as_data()["business_registered_on_companies_house"][0].code == "required"

    def test_optional_choice_removed(self, request_object):
        form = forms.IsTheBusinessRegisteredWithCompaniesHouseForm(request=request_object)
        assert len(form.fields["business_registered_on_companies_house"].choices) == len(choices.YesNoDoNotKnowChoices.choices)


class TestDoYouKnowTheRegisteredCompanyNumberForm:
    def test_do_you_know_the_registered_company_number_required(self, post_request_object):
        form = forms.DoYouKnowTheRegisteredCompanyNumberForm(
            data={"do_you_know_the_registered_company_number": None}, request=post_request_object
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

    @patch("apply_for_a_licence.forms.forms_business.get_details_from_companies_house")
    @patch("apply_for_a_licence.forms.forms_business.get_formatted_address")
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
        assert form.cleaned_data["url_location"] == "in_the_uk"

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
    def test_required(self, post_request_object):
        form = forms.BusinessAddedForm(data={"do_you_want_to_add_another_business": None}, request=post_request_object)
        assert not form.is_valid()
        assert "do_you_want_to_add_another_business" in form.errors
        assert form.errors.as_data()["do_you_want_to_add_another_business"][0].code == "required"

    def test_never_bound(self, request_object):
        form = forms.BusinessAddedForm(data={"do_you_want_to_add_another_business": "Yes"}, request=request_object)
        assert not form.is_bound
