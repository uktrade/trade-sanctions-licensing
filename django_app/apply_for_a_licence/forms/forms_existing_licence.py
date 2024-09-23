from typing import Any

from apply_for_a_licence.models import Licence
from apply_for_a_licence.utils import get_cleaned_data_for_step
from core.forms.base_forms import BaseModelForm
from crispy_forms_gds.layout import (
    ConditionalQuestion,
    ConditionalRadios,
    Field,
    Fluid,
    Layout,
    Size,
)


class ExistingLicencesForm(BaseModelForm):
    hide_optional_label_fields = ["existing_licences"]

    class Meta:
        model = Licence
        fields = ("held_existing_licence", "existing_licences")
        labels = {
            "existing_licences": "Enter all previous licence numbers",
        }
        help_texts = {"held_existing_licence": "Your application may be delayed if you do not give all previous licence numbers"}

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["held_existing_licence"].empty_label = None
        # todo - abstract the following logic to apply to all ConditionalRadios forms
        self.helper.legend_tag = "h1"
        self.helper.legend_size = Size.LARGE
        self.helper.label_tag = ""
        self.helper.label_size = None
        self.helper.layout = Layout(
            ConditionalRadios(
                "held_existing_licence",
                ConditionalQuestion(
                    "Yes",
                    Field.text("existing_licences", field_width=Fluid.TWO_THIRDS),
                ),
                "No",
            )
        )
        self.held_existing_licence_label = (
            "Have any of the businesses you've added held a licence before to provide "
            "any sanctioned services or export any sanctioned goods?"
        )

        if start_view := get_cleaned_data_for_step(self.request, "start"):
            if start_view.get("who_do_you_want_the_licence_to_cover") == "myself":
                self.held_existing_licence_label = (
                    "Have you, or has anyone else you've added, held a licence before "
                    "to provide any sanctioned services or export any sanctioned goods?"
                )
            elif start_view.get("who_do_you_want_the_licence_to_cover") == "individual":
                self.held_existing_licence_label = (
                    "Have any of the individuals you've added held a licence before to "
                    "provide any sanctioned services or export any sanctioned goods?"
                )
        self.fields["held_existing_licence"].label = self.held_existing_licence_label

    def clean(self) -> dict[str, Any]:
        start_view = get_cleaned_data_for_step(self.request, "start")
        cleaned_data = super().clean()
        if cleaned_data.get("held_existing_licence") == "yes" and not cleaned_data["existing_licences"]:
            self.add_error("existing_licences", "Enter previous licence numbers")

        if cleaned_data.get("held_existing_licence") != "yes" and not "no":
            if start_view.get("who_do_you_want_the_licence_to_cover") == "business":
                self.add_error(
                    "held_existing_licence",
                    "Select yes if any of the businesses have held a licence before to "
                    "provide sanctioned services or export sanctioned goods",
                )
            elif start_view.get("who_do_you_want_the_licence_to_cover") == "individual":
                self.add_error(
                    "held_existing_licence",
                    "Select yes if any of the individuals have held a licence before to "
                    "provide sanctioned services or export sanctioned goods",
                )
            elif start_view.get("who_do_you_want_the_licence_to_cover") == "myself":
                self.add_error(
                    "held_existing_licence",
                    "Select yes if you, or anyone else you've added, has held a licence before to "
                    "provide sanctioned services or export sanctioned goods",
                )

        if cleaned_data.get("held_existing_licence") == "no":
            cleaned_data["existing_licences"] = None
        return cleaned_data
