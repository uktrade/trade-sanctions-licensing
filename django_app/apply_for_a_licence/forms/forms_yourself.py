from apply_for_a_licence.models import Individual, Organisation
from core.forms.base_forms import (
    BaseModelForm,
    BaseNonUKBusinessDetailsForm,
    BaseUKBusinessDetailsForm,
)
from crispy_forms_gds.layout import Field, Fluid, Layout, Size
from django import forms


class AddYourselfForm(BaseModelForm):
    form_h1_header = "Your details"
    nationality = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Individual
        fields = [
            "first_name",
            "last_name",
            "nationality_and_location",
        ]
        widgets = {"first_name": forms.TextInput, "last_name": forms.TextInput, "nationality_and_location": forms.RadioSelect}
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "nationality_and_location": "What is your nationality and location?",
        }
        error_messages = {
            "first_name": {"required": "Enter first name"},
            "last_name": {"required": "Enter last name"},
            "nationality_and_location": {"required": "Select your nationality and location"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["nationality_and_location"].choices.pop(0)
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout(
            Field.text("first_name", field_width=Fluid.ONE_THIRD),
            Field.text("last_name", field_width=Fluid.ONE_THIRD),
            Field.radios("nationality_and_location", legend_size=Size.MEDIUM, legend_tag="h2"),
        )

    def clean(self):
        cleaned_data = super().clean()
        if self.cleaned_data.get("nationality_and_location", None):
            cleaned_data["nationality"] = dict(self.fields["nationality_and_location"].choices)[
                self.cleaned_data["nationality_and_location"]
            ]
        return cleaned_data


class AddYourselfUKAddressForm(BaseUKBusinessDetailsForm):
    form_h1_header = "What is your home address?"

    class Meta(BaseUKBusinessDetailsForm.Meta):
        model = Organisation
        fields = (
            "town_or_city",
            "country",
            "address_line_1",
            "address_line_2",
            "county",
            "postcode",
        )
        widgets = BaseUKBusinessDetailsForm.Meta.widgets
        labels = BaseUKBusinessDetailsForm.Meta.labels
        error_messages = BaseUKBusinessDetailsForm.Meta.error_messages | {
            "address_line_1": {"required": "Enter address line 1, typically the building and street"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Field.text("country", field_width=Fluid.TWO_THIRDS),
            Field.text("address_line_1", field_width=Fluid.TWO_THIRDS),
            Field.text("address_line_2", field_width=Fluid.TWO_THIRDS),
            Field.text("town_or_city", field_width=Fluid.ONE_HALF),
            Field.text("county", field_width=Fluid.ONE_HALF),
            Field.text("postcode", field_width=Fluid.ONE_THIRD),
        )


class AddYourselfNonUKAddressForm(BaseNonUKBusinessDetailsForm):
    form_h1_header = "What is your home address?"

    class Meta(BaseNonUKBusinessDetailsForm.Meta):
        model = Organisation
        fields = (
            "town_or_city",
            "country",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "county",
            "postcode",
        )
        widgets = BaseNonUKBusinessDetailsForm.Meta.widgets
        labels = BaseNonUKBusinessDetailsForm.Meta.labels
        error_messages = BaseNonUKBusinessDetailsForm.Meta.error_messages | {
            "address_line_1": {"required": "Enter address line 1"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Field.text("country", field_width=Fluid.TWO_THIRDS),
            Field.text("town_or_city", field_width=Fluid.TWO_THIRDS),
            Field.text("address_line_1", field_width=Fluid.TWO_THIRDS),
            Field.text("address_line_2", field_width=Fluid.TWO_THIRDS),
            Field.text("address_line_3", field_width=Fluid.TWO_THIRDS),
            Field.text("address_line_4", field_width=Fluid.TWO_THIRDS),
        )
