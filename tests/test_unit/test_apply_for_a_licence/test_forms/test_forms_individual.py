from apply_for_a_licence.forms import forms_individual as forms


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
