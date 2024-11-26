from apply_for_a_licence.choices import LicensingGroundsChoices
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

    def test_checkbox_or(self, request_object):
        form = forms.LicensingGroundsForm(data={"licensing_grounds": None}, request=request_object)
        assert form.checkbox_choices[-3].divider == "or"
        assert form.checkbox_choices[-2][0] == "Unknown grounds"
        assert form.checkbox_choices[-1][0] == "None of these"


class TestPurposeOfProvisionForm:
    def test_required(self, request_object):
        form = forms.PurposeOfProvisionForm(data={"purpose_of_provision": None}, request=request_object)
        assert not form.is_valid()
        assert "purpose_of_provision" in form.errors
        assert form.errors.as_data()["purpose_of_provision"][0].code == "required"
