from apply_for_a_licence.forms import forms_start as forms
from django import forms as django_forms


class TestSubmitterReferenceForm:
    def test_save(self, request_object, test_apply_user):
        form = forms.SubmitterReferenceForm(data={"submitter_reference": "123456"}, request=request_object)
        assert form.is_valid()
        instance = form.save()
        assert instance.submitter_reference == "123456"
        assert instance.user == test_apply_user


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
        assert "is_third_party" in form.errors
        assert form.errors.as_data()["is_third_party"][0].code == "required"


class TestYourDetailsForm:
    def test_required(self):
        form = forms.YourDetailsForm(data={"applicant_full_name": None})
        assert not form.is_valid()
        assert "applicant_full_name" in form.errors
        assert form.errors.as_data()["applicant_full_name"][0].code == "required"
