from typing import Any

from core.forms.base_forms import BaseForm, BaseModelForm
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import (
    ConditionalQuestion,
    ConditionalRadios,
    Field,
    Fluid,
    Layout,
    Size,
)
from django import forms

from . import choices
from .choices import YES_NO_CHOICES
from .models import Licence


class StartForm(BaseModelForm):
    class Meta:
        model = Licence
        fields = ["who_do_you_want_the_licence_to_cover"]
        widgets = {
            "who_do_you_want_the_licence_to_cover": forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        CHOICES = (
            Choice(
                choices.WhoDoYouWantTheLicenceToCoverChoices.business.value,
                choices.WhoDoYouWantTheLicenceToCoverChoices.business.label,
                hint="The licence will cover all employees, members, partners, consultants, officers and directors",
            ),
            Choice(
                choices.WhoDoYouWantTheLicenceToCoverChoices.individual.value,
                choices.WhoDoYouWantTheLicenceToCoverChoices.individual.label,
                hint="The licence will cover the named individuals only but not the business they work for",
            ),
            Choice(
                choices.WhoDoYouWantTheLicenceToCoverChoices.myself.value,
                choices.WhoDoYouWantTheLicenceToCoverChoices.myself.label,
                hint="You can add other named individuals if they will be providing the services with you",
            ),
        )
        self.fields["who_do_you_want_the_licence_to_cover"].choices = CHOICES


class ThirdPartyForm(BaseForm):
    are_you_applying_on_behalf_of_someone_else = forms.TypedChoiceField(
        choices=YES_NO_CHOICES,
        coerce=lambda x: x == "True",
        widget=forms.RadioSelect,
        label="Are you a third-party applying on behalf of a business you represent?",
        error_messages={"required": "Select yes if you're a third party applying on behalf of a business you represent"},
    )


class WhatIsYourEmailForm(BaseForm):
    email = forms.EmailField(
        label="What is your email address?",
        error_messages={
            "required": "Enter your email address",
            "invalid": "Enter a valid email address",
        },
    )


class PreviousLicenceForm(BaseModelForm):
    hide_optional_label_fields = ["previous_licences"]

    class Meta:
        model = Licence
        fields = ("held_previous_licence", "previous_licences")
        labels = {
            "held_previous_licence": "held a licence before to provide sanctioned services?",
            "previous_licences": "Enter all previous licence numbers",
        }
        error_messages = {
            "held_previous_licence": {
                "required": "Select yes if the business has held a licence before to provide these services"
            },
            "previous_licences": {"required": "Licence number cannot be blank"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["held_previous_licence"].empty_label = None
        # todo - abstract the following logic to apply to all ConditionalRadios forms
        self.helper.legend_tag = "h1"
        self.helper.legend_size = Size.LARGE
        self.helper.label_tag = ""
        self.helper.label_size = None
        self.helper.layout = Layout(
            ConditionalRadios(
                "held_previous_licence",
                ConditionalQuestion(
                    "Yes",
                    Field.text("previous_licences", field_width=Fluid.TWO_THIRDS),
                ),
                "No",
            )
        )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if cleaned_data.get("held_previous_licence") == "yes" and not cleaned_data["previous_licences"]:
            self.add_error("previous_licences", self.Meta.error_messages["previous_licences"]["required"])
        return cleaned_data
