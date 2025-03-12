from apply_for_a_licence import choices
from apply_for_a_licence.forms import forms_individual as forms
from apply_for_a_licence.models import Individual, Licence


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
    def test_required(self, post_request_object):
        form = forms.IndividualAddedForm({}, request=post_request_object)
        assert not form.is_valid()
        assert "do_you_want_to_add_another_individual" in form.errors
        assert form.errors.as_data()["do_you_want_to_add_another_individual"][0].code == "required"

    def test_incomplete_individual_raises_error(self, post_request_object, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user,
            who_do_you_want_the_licence_to_cover=choices.WhoDoYouWantTheLicenceToCoverChoices.individual.value,
        )
        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        Individual.objects.create(
            licence=licence,
            status="draft",
        )

        form = forms.IndividualAddedForm(
            data={"do_you_want_to_add_another_individual": "Yes"}, request=post_request_object, licence_object=licence
        )
        assert form.errors.as_data()["__all__"][0].code == "incomplete_individual"


class TestBusinessEmployingIndividualForm:
    def test_required(self, request_object):
        form = forms.BusinessEmployingIndividualForm(data={}, request=request_object)
        assert not form.is_valid()
        assert "name" in form.errors
        assert form.errors.as_data()["name"][0].code == "required"
