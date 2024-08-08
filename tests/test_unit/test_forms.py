from unittest.mock import patch

from apply_for_a_licence.forms import WhichSanctionsRegimeForm


class TestSanctionsRegimeForm:
    def test_required(self, request_object):
        form = WhichSanctionsRegimeForm(data={"which_sanctions_regime": None}, request=request_object)
        assert not form.is_valid()
        assert "which_sanctions_regime" in form.errors
        assert form.has_error("which_sanctions_regime", "required")

    @patch(
        "apply_for_a_licence.forms.active_regimes",
        [
            {"name": "test regime", "is_active": True},
            {"name": "test regime1", "is_active": True},
            {"name": "test regime2", "is_active": True},
        ],
    )
    def test_choices_creation(self, request_object):
        form = WhichSanctionsRegimeForm(request=request_object)
        assert len(form.fields["which_sanctions_regime"].choices) == 3
        flat_choices = [choice[0] for choice in form.fields["which_sanctions_regime"].choices]
        assert "test regime" in flat_choices
        assert "test regime1" in flat_choices
        assert "test regime2" in flat_choices

    @patch(
        "apply_for_a_licence.forms.active_regimes",
        [
            {"name": "test regime", "is_active": True},
        ],
    )
    def test_assert_unknown_regime_selected_error(self, request_object):
        form = WhichSanctionsRegimeForm(
            data={"which_sanctions_regime": ["Unknown Regime", "test regime"]}, request=request_object
        )
        assert not form.is_valid()
        assert "which_sanctions_regime" in form.errors
        assert form.has_error("which_sanctions_regime", "invalid_choice")

    @patch(
        "apply_for_a_licence.forms.active_regimes",
        [
            {"name": "Russia regime", "is_active": True},
            {"name": "Belarus regime", "is_active": True},
            {"name": "Cuba regime", "is_active": True},
        ],
    )
    def test_slimmed_down_choices(self, request_object):
        session = request_object.session
        session["TypeOfServiceView"] = {"type_of_service": "internet"}
        session.save()
        form = WhichSanctionsRegimeForm(request=request_object)
        assert len(form.fields["which_sanctions_regime"].choices) == 2
        flat_choices = [choice[0] for choice in form.fields["which_sanctions_regime"].choices]
        assert "Russia regime" in flat_choices
        assert "Belarus regime" in flat_choices
        assert "Cuba regime" not in flat_choices
