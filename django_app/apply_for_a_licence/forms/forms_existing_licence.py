from typing import Any

from apply_for_a_licence.models import ExistingLicences
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
    hide_optional_label_fields = ["licences"]

    class Meta:
        model = ExistingLicences
        fields = ("held_existing_licence", "licences")
        labels = {
            "licences": "Enter all previous licence numbers",
        }
        error_messages = {
            "held_existing_licence": {
                "required": "Select yes if the business has held a licence before to provide these services"
            },
            "licences": {"required": "Licence number cannot be blank"},
        }

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
                    Field.text("licences", field_width=Fluid.TWO_THIRDS),
                ),
                "No",
            )
        )
        self.held_existing_licence_label = (
            "Have any of the businesses you've added held a licence before to provide sanctioned services?"
        )

        if start_view := self.request.session.get("StartView", False):
            if start_view.get("who_do_you_want_the_licence_to_cover") == "myself":
                self.held_existing_licence_label = (
                    "Have you, or has anyone else you've added, held a licence before to provide sanctioned services?"
                )
            elif start_view.get("who_do_you_want_the_licence_to_cover") == "individual":
                self.held_existing_licence_label = (
                    "Have any of the individuals you've added held a licence before to provide sanctioned services?"
                )
        self.fields["held_existing_licence"].label = self.held_existing_licence_label

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if cleaned_data.get("held_existing_licence") == "yes" and not cleaned_data["licences"]:
            self.add_error("licences", self.Meta.error_messages["licences"]["required"])
        return cleaned_data
