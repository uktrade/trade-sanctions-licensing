from unittest.mock import patch

from apply_for_a_licence.forms import forms_services as forms


class TestTypeOfServiceForm:
    def test_required(self, request_object):
        form = forms.TypeOfServiceForm(data={"type_of_service": None}, request=request_object)
        assert not form.is_valid()
        assert "type_of_service" in form.errors
        assert form.errors.as_data()["type_of_service"][0].code == "required"


class TestSanctionsRegimeForm:
    def test_required(self, request_object):
        form = forms.WhichSanctionsRegimeForm(data={"regimes": None}, request=request_object)
        assert not form.is_valid()
        assert "regimes" in form.errors
        assert form.has_error("regimes", "required")

    @patch(
        "apply_for_a_licence.forms.forms_services.get_active_regimes",
        return_value=[
            {"name": "test regime", "is_active": True},
            {"name": "test regime1", "is_active": True},
            {"name": "test regime2", "is_active": True},
        ],
    )
    def test_choices_creation(self, request_object):
        form = forms.WhichSanctionsRegimeForm(request=request_object)
        assert len(form.fields["regimes"].choices) == 3
        flat_choices = [choice[0] for choice in form.fields["regimes"].choices]
        assert "test regime" in flat_choices
        assert "test regime1" in flat_choices
        assert "test regime2" in flat_choices

    @patch(
        "apply_for_a_licence.forms.forms_services.get_active_regimes",
        return_value=[
            {"name": "test regime", "is_active": True},
        ],
    )
    def test_assert_unknown_regime_selected_error(self, request_object):
        form = forms.WhichSanctionsRegimeForm(
            data={"which_sanctions_regime": ["Unknown Regime", "test regime"]}, request=request_object
        )
        assert not form.is_valid()
        assert "which_sanctions_regime" in form.errors
        assert form.has_error("which_sanctions_regime", "invalid_choice")


class TestProfessionalOrBusinessServicesForm:
    def test_required(self, request_object):
        form = forms.ProfessionalOrBusinessServicesForm(data={"professional_or_business_services": None}, request=request_object)
        assert not form.is_valid()
        assert "professional_or_business_services" in form.errors
        assert form.errors.as_data()["professional_or_business_services"][0].code == "required"


class TestServiceActivitiesForm:
    def test_required(self, request_object):
        form = forms.ServiceActivitiesForm(data={"service_activities": None}, request=request_object)
        assert not form.is_valid()
        assert "service_activities" in form.errors
        assert form.errors.as_data()["service_activities"][0].code == "required"
