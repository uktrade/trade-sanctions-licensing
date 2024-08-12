from apply_for_a_licence.forms import forms_existing_licence as forms


class TestExistingLicencesForm:
    def test_required(self, request_object):
        form = forms.ExistingLicencesForm(data={"held_existing_licence": None}, request=request_object)
        assert not form.is_valid()
        assert "held_existing_licence" in form.errors
        assert form.errors.as_data()["held_existing_licence"][0].code == "required"
