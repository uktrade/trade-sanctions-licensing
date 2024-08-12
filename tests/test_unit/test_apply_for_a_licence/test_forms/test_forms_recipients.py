from apply_for_a_licence.forms import forms_recipients as forms


class TestWhereIsTheRecipientLocatedForm:
    def test_required(self, request_object):
        form = forms.WhereIsTheRecipientLocatedForm(data={"where_is_the_address": None}, request=request_object)
        assert not form.is_valid()
        assert "where_is_the_address" in form.errors
        assert form.errors.as_data()["where_is_the_address"][0].code == "required"


class TestAddARecipientForm:
    def test_uk_required(self):
        form = forms.AddARecipientForm(data={}, is_uk_address=True)
        assert not form.is_valid()
        assert "name" in form.errors
        assert "town_or_city" in form.errors
        assert "address_line_1" in form.errors
        assert "postcode" in form.errors
        assert form.errors.as_data()["name"][0].code == "required"
        assert form.errors.as_data()["town_or_city"][0].code == "required"
        assert form.errors.as_data()["address_line_1"][0].code == "required"
        assert form.errors.as_data()["postcode"][0].code == "required"

    def test_uk_valid(self):
        form = forms.AddARecipientForm(
            data={"name": "Business", "town_or_city": "London", "address_line_1": "40 Hollyhead", "postcode": "SW1A 1AA"},
            is_uk_address=True,
        )
        assert form.is_valid()

    def test_non_uk_required(self):
        form = forms.AddARecipientForm(data={}, is_uk_address=False)
        assert not form.is_valid()
        assert "name" in form.errors
        assert "country" in form.errors
        assert form.errors.as_data()["name"][0].code == "required"
        assert form.errors.as_data()["country"][0].code == "required"

    def test_non_uk_valid(self):
        form = forms.AddARecipientForm(
            data={
                "name": "Business",
                "country": "BE",
                "town_or_city": "Leuven",
                "address_line_1": "Sesteenweg",
            },
            is_uk_address=False,
        )
        assert form.is_valid()

    def test_incorrect_postcode_validation(self):

        form = forms.AddARecipientForm(data={"postcode": "123"}, is_uk_address=True)
        assert not form.is_valid()
        assert "postcode" in form.errors
        assert form.errors.as_data()["postcode"][0].code == "invalid"


class TestRecipientAddedForm:
    def test_required(self, request_object):
        form = forms.RecipientAddedForm(data={"do_you_want_to_add_another_recipient": None}, request=request_object)
        assert not form.is_valid()
        assert "do_you_want_to_add_another_recipient" in form.errors
        assert form.errors.as_data()["do_you_want_to_add_another_recipient"][0].code == "required"


class TestRelationshipProviderRecipientForm:
    def test_required(self, request_object):
        form = forms.RelationshipProviderRecipientForm(data={"relationship": None}, request=request_object)
        assert not form.is_valid()
        assert "relationship" in form.errors
        assert form.errors.as_data()["relationship"][0].code == "required"
