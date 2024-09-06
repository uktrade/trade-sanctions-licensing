from apply_for_a_licence.models import Individual, Organisation
from core.forms.base_forms import (
    BaseBusinessDetailsForm,
    BaseForm,
    BaseModelForm,
    BaseNonUKBusinessDetailsForm,
    BaseUKBusinessDetailsForm,
)
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import Field, Fieldset, Fluid, Layout, Size
from django import forms


class AddAnIndividualForm(BaseModelForm):
    form_h1_header = "Add an individual"

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
            "nationality_and_location": "What is the individual's nationality and location?",
        }
        error_messages = {
            "first_name": {"required": "Enter your first name"},
            "last_name": {"required": "Enter your last name"},
            "nationality_and_location": {"required": "Enter your nationality and location"},
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


class IndividualAddedForm(BaseForm):
    revalidate_on_done = False

    do_you_want_to_add_another_individual = forms.TypedChoiceField(
        choices=(
            Choice(True, "Yes"),
            Choice(False, "No"),
        ),
        coerce=lambda x: x == "True",
        label="Do you want to add another individual?",
        error_messages={"required": "Select yes if you want to add another individual"},
        widget=forms.RadioSelect,
        required=True,
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.legend_size = Size.MEDIUM
        self.helper.legend_tag = None

        if self.request.method == "GET":
            self.is_bound = False


class BusinessEmployingIndividualForm(BaseBusinessDetailsForm):
    form_h1_header = "Details of the business employing the individual[s]"

    class Meta(BaseBusinessDetailsForm.Meta):
        model = Organisation
        fields = (
            "name",
            "country",
            "town_or_city",
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

        self.helper.layout = Layout(
            Fieldset(
                Field.text("name", field_width=Fluid.TWO_THIRDS),
                legend="Name",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Fieldset(
                Field.text("country", field_width=Fluid.TWO_THIRDS),
                Field.text("town_or_city", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_1", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_2", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_3", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_4", field_width=Fluid.TWO_THIRDS),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
        )


class IndividualUKAddressForm(BaseUKBusinessDetailsForm):
    form_h1_header = "What is the individual's address?"

    class Meta(BaseUKBusinessDetailsForm.Meta):
        model = Individual
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
        error_messages = BaseUKBusinessDetailsForm.Meta.error_messages

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Field.text("address_line_1", field_width=Fluid.TWO_THIRDS),
            Field.text("address_line_2", field_width=Fluid.TWO_THIRDS),
            Field.text("town_or_city", field_width=Fluid.ONE_HALF),
            Field.text("county", field_width=Fluid.ONE_HALF),
            Field.text("postcode", field_width=Fluid.ONE_THIRD),
        )

        self.helper.label_size = None


class IndividualNonUKAddressForm(BaseNonUKBusinessDetailsForm):
    form_h1_header = "What is the individual's address?"

    class Meta(BaseNonUKBusinessDetailsForm.Meta):
        model = Individual
        fields = (
            "town_or_city",
            "country",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
        )
        widgets = BaseUKBusinessDetailsForm.Meta.widgets
        labels = BaseUKBusinessDetailsForm.Meta.labels
        error_messages = BaseUKBusinessDetailsForm.Meta.error_messages

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Field.text("country", field_width=Fluid.TWO_THIRDS),
            Field.text("town_or_city", field_width=Fluid.TWO_THIRDS),
            Field.text("address_line_1", field_width=Fluid.TWO_THIRDS),
            Field.text("address_line_2", field_width=Fluid.TWO_THIRDS),
            Field.text("address_line_3", field_width=Fluid.TWO_THIRDS),
            Field.text("address_line_4", field_width=Fluid.TWO_THIRDS),
        )

        self.helper.label_size = None
