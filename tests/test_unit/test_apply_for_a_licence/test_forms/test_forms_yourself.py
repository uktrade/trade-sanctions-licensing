from apply_for_a_licence.forms import forms_yourself as forms


class TestAddYourselfForm:
    def test_required(self, request_object):
        form = forms.AddYourselfForm(
            data={"first_name": None, "last_name": None, "nationality_and_location": None}, request=request_object
        )
        assert not form.is_valid()
        assert "first_name" in form.errors
        assert "last_name" in form.errors
        assert "nationality_and_location" in form.errors
        assert form.errors.as_data()["first_name"][0].code == "required"
        assert form.errors.as_data()["last_name"][0].code == "required"
        assert form.errors.as_data()["nationality_and_location"][0].code == "required"


class TestAddYourselfUKAddressForm:
    def test_required(self):
        form = forms.AddYourselfUKAddressForm(data={})
        assert not form.is_valid()
        assert "town_or_city" in form.errors
        assert "address_line_1" in form.errors
        assert "postcode" in form.errors
        assert form.errors.as_data()["town_or_city"][0].code == "required"
        assert form.errors.as_data()["address_line_1"][0].code == "required"
        assert form.errors.as_data()["postcode"][0].code == "required"

    def test_valid(self):
        form = forms.AddYourselfUKAddressForm(
            data={"town_or_city": "London", "address_line_1": "40 Hollyhead", "postcode": "SW1A 1AA"}
        )
        assert form.is_valid()

    def test_incorrect_postcode_validation(self):

        form = forms.AddYourselfUKAddressForm(data={"postcode": "123"})
        assert not form.is_valid()
        assert "postcode" in form.errors
        assert form.errors.as_data()["postcode"][0].code == "invalid"


class TestAddYourselfNonUKAddressForm:
    def test_required(self):
        form = forms.AddYourselfNonUKAddressForm(data={"country": None})
        assert not form.is_valid()
        assert "town_or_city" in form.errors
        assert "address_line_1" in form.errors
        assert "country" in form.errors
        assert form.errors.as_data()["country"][0].code == "required"
        assert form.errors.as_data()["town_or_city"][0].code == "required"
        assert form.errors.as_data()["address_line_1"][0].code == "required"

    def test_non_uk_valid(self):
        form = forms.AddYourselfNonUKAddressForm(
            data={"country": "BE", "town_or_city": "Brussels", "address_line_1": "Rue Neuve"}
        )
        assert form.is_valid()
