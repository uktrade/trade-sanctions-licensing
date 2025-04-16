from apply_for_a_licence.forms import forms_existing_licence as forms


class TestExistingLicencesForm:
    def test_required(self, request_object):
        form = forms.ExistingLicencesForm(data={"held_existing_licence": None}, request=request_object)
        assert not form.is_valid()
        assert "held_existing_licence" in form.errors
        assert form.errors.as_data()["held_existing_licence"][0].code == "required"

    def test_label_myself_licence(self, request_object, yourself_licence):
        form = forms.ExistingLicencesForm(
            data={"held_existing_licence": "yes"}, request=request_object, instance=yourself_licence
        )
        assert form.fields["held_existing_licence"].label == (
            "Have you, or has anyone else you've added, held a "
            "licence before to provide any sanctioned services "
            "or export any sanctioned goods?"
        )

    def test_required_error_myself_licence(self, request_object, yourself_licence):
        form = forms.ExistingLicencesForm(data={"held_existing_licence": None}, request=request_object, instance=yourself_licence)
        assert not form.is_valid()
        assert "held_existing_licence" in form.errors
        held_existing_licence_error = form.errors.as_data()["held_existing_licence"][0]

        assert held_existing_licence_error.code == "required"
        assert held_existing_licence_error.message == (
            "Select yes if you, or anyone else you've added, has held a "
            "licence before to provide sanctioned services or export "
            "sanctioned goods"
        )

    def test_label_individual_licence(self, request_object, individual_licence):
        form = forms.ExistingLicencesForm(
            data={"held_existing_licence": "yes"}, request=request_object, instance=individual_licence
        )
        assert form.fields["held_existing_licence"].label == (
            "Have any of the individuals you've added held a "
            "licence before to provide any sanctioned services "
            "or export any sanctioned goods?"
        )

    def test_required_error_individual_licence(self, request_object, individual_licence):
        form = forms.ExistingLicencesForm(
            data={"held_existing_licence": None}, request=request_object, instance=individual_licence
        )
        assert not form.is_valid()
        assert "held_existing_licence" in form.errors
        held_existing_licence_error = form.errors.as_data()["held_existing_licence"][0]
        assert held_existing_licence_error.code == "required"
        assert held_existing_licence_error.message == (
            "Select yes if any of the individuals have held a licence "
            "before to provide sanctioned services "
            "or export sanctioned goods"
        )

    def test_label_business_licence(self, request_object, business_licence):
        form = forms.ExistingLicencesForm(
            data={"held_existing_licence": "yes"}, request=request_object, instance=business_licence
        )
        assert form.fields["held_existing_licence"].label == (
            "Have any of the businesses you've added held a licence before to provide "
            "any sanctioned services or export any sanctioned goods?"
        )

    def test_required_error_business_licence(self, request_object, business_licence):
        form = forms.ExistingLicencesForm(data={"held_existing_licence": None}, request=request_object, instance=business_licence)
        assert not form.is_valid()
        assert "held_existing_licence" in form.errors
        held_existing_licence_error = form.errors.as_data()["held_existing_licence"][0]
        assert held_existing_licence_error.code == "required"
        assert held_existing_licence_error.message == (
            "Select yes if any of the businesses have held a licence before to provide sanctioned services or "
            "export sanctioned goods"
        )

    def test_required_licence_number_if_yes(self, request_object):
        form = forms.ExistingLicencesForm(data={"held_existing_licence": "yes"}, request=request_object)
        assert not form.is_valid()
        assert "existing_licences" in form.errors
        assert form.errors.as_data()["existing_licences"][0].code == "required"

    def test_cleaned_data_no_licence_number(self):
        form = forms.ExistingLicencesForm(data={"held_existing_licence": "no"})
        assert form.is_valid()
        assert not form.cleaned_data["existing_licences"]
