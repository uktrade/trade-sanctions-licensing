from apply_for_a_licence.choices import (
    LicensingGroundsChoices,
    ProfessionalOrBusinessServicesChoices,
    TypeOfServicesChoices,
)
from apply_for_a_licence.forms import forms_grounds_purpose as forms


class TestLicensingGroundsForm:
    def test_required(self, request_object):
        form = forms.LicensingGroundsForm(data={"licensing_grounds": None}, request=request_object)
        assert not form.is_valid()
        assert "licensing_grounds" in form.errors
        assert form.errors.as_data()["licensing_grounds"][0].code == "required"
        assert LicensingGroundsChoices.parent_or_subsidiary_company.value not in [
            each[0] for each in form.fields["licensing_grounds"].choices
        ]

    def test_required_professional_business_service_non_legal(self, request_object, business_licence):
        business_licence.type_of_service = TypeOfServicesChoices.professional_and_business
        business_licence.professional_or_business_services = [ProfessionalOrBusinessServicesChoices.accounting]
        business_licence.save()
        form = forms.LicensingGroundsForm(data={"licensing_grounds": None}, request=request_object, instance=business_licence)

        assert not form.is_valid()
        assert "licensing_grounds" in form.errors
        licensing_grounds = form.errors.as_data()["licensing_grounds"][0]
        assert licensing_grounds.code == "required"
        assert licensing_grounds.message == (
            "Select which licensing grounds describe your purpose for providing "
            "the sanctioned services, or select none of these, or select I do not know"
        )

    def test_required_professional_business_service_legal(self, request_object, business_licence):
        business_licence.type_of_service = TypeOfServicesChoices.professional_and_business
        business_licence.professional_or_business_services = [ProfessionalOrBusinessServicesChoices.legal_advisory]
        business_licence.save()
        form = forms.LicensingGroundsForm(data={"licensing_grounds": None}, request=request_object, instance=business_licence)

        assert not form.is_valid()
        assert "licensing_grounds" in form.errors
        licensing_grounds = form.errors.as_data()["licensing_grounds"][0]
        assert licensing_grounds.code == "required"
        assert licensing_grounds.message == (
            "Select which licensing grounds describe the purpose of the relevant activity for which the legal advice "
            "is being given, or select none of these, or select I do not know"
        )

    def test_checkbox_or(self, request_object):
        form = forms.LicensingGroundsForm(data={"licensing_grounds": None}, request=request_object)
        assert form.checkbox_choices[-3].divider == "or"
        assert form.checkbox_choices[-2][0] == "unknown"
        assert form.checkbox_choices[-1][0] == "none"


class TestPurposeOfProvisionForm:
    def test_required(self, request_object):
        form = forms.PurposeOfProvisionForm(data={"purpose_of_provision": None}, request=request_object)
        assert not form.is_valid()
        assert "purpose_of_provision" in form.errors
        assert form.errors.as_data()["purpose_of_provision"][0].code == "required"
