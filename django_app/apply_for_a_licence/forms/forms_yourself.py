from apply_for_a_licence.models import Individual, Organisation
from core.forms.base_forms import BaseBusinessDetailsForm, BaseModelForm
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
        help_texts = {"nationality_and_location": "Hint text"}
        error_messages = {"first_name": {"required": "Enter your first name"}, "last_name": {"required": "Enter your last name"}}

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


class AddYourselfAddressForm(BaseBusinessDetailsForm):
    form_h1_header = "What is your work address?"

    class Meta(BaseBusinessDetailsForm.Meta):
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
        widgets = BaseBusinessDetailsForm.Meta.widgets
        labels = BaseBusinessDetailsForm.Meta.labels
        error_messages = BaseBusinessDetailsForm.Meta.error_messages

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        self.fields["town_or_city"].required = True
        self.fields["address_line_1"].required = True

        self.helper.layout = Layout(
            Field.text("town_or_city", field_width=Fluid.ONE_THIRD),
            Field.text("country", field_width=Fluid.ONE_THIRD),
            Field.text("address_line_1", field_width=Fluid.ONE_THIRD),
            Field.text("address_line_2", field_width=Fluid.ONE_THIRD),
            Field.text("address_line_3", field_width=Fluid.ONE_THIRD),
            Field.text("address_line_4", field_width=Fluid.ONE_THIRD),
            Field.text("county", field_width=Fluid.ONE_THIRD),
            Field.text("postcode", field_width=Fluid.ONE_THIRD),
        )
