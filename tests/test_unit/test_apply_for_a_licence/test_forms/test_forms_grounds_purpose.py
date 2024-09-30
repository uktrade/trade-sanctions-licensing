from unittest.mock import patch

from apply_for_a_licence.choices import LicensingGroundsChoices
from apply_for_a_licence.forms import forms_grounds_purpose as forms


class TestLicensingGroundsForm:
    def test_required(self, request_object):
        form = forms.LicensingGroundsForm(data={"licensing_grounds": None}, request=request_object)
        assert not form.is_valid()
        assert "licensing_grounds" in form.errors
        assert form.errors.as_data()["licensing_grounds"][0].code == "required"

    @patch("apply_for_a_licence.forms.forms_grounds_purpose.LicensingGroundsForm.get_services")
    def test_audit_service_selected(self, mocked_get_services, request_object):
        normal_form = forms.LicensingGroundsForm(request=request_object)
        mocked_get_services.return_value = ["auditing"]
        audit_form = forms.LicensingGroundsForm(request=request_object)

        assert len(audit_form.fields["licensing_grounds"].choices) == len(normal_form.fields["licensing_grounds"].choices) - 1
        assert LicensingGroundsChoices.parent_or_subsidiary_company.value not in [
            each[0] for each in audit_form.fields["licensing_grounds"].choices
        ]


class TestPurposeOfProvisionForm:
    def test_required(self, request_object):
        form = forms.PurposeOfProvisionForm(data={"purpose_of_provision": None}, request=request_object)
        assert not form.is_valid()
        assert "purpose_of_provision" in form.errors
        assert form.errors.as_data()["purpose_of_provision"][0].code == "required"
