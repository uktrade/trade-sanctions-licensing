from apply_for_a_licence import choices
from apply_for_a_licence.models import ApplicationServices, Ground
from core.crispy_fields import get_field_with_label_id
from core.forms.base_forms import BaseForm, BaseModelForm
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import Field, Fieldset, Layout
from django import forms


class LicensingGroundsForm(BaseForm):
    form_h1_header = "Which of these licensing grounds describes your purpose for providing the sanctioned services?"
    licensing_grounds = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=choices.LicensingGroundsChoices.choices,
        required=True,
        label="Select all that apply",
        error_messages={
            "required": "Select the licensing grounds",
            "invalid": "Select the licensing grounds or select I do not know",
        },
    )

    class Meta:
        model = Ground
        fields = ["licensing_grounds"]

    class Media:
        js = ["apply_for_a_licence/javascript/licensing_grounds.js"]

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.legal_advisory = kwargs.pop("legal_advisory", False)
        super().__init__(*args, **kwargs)
        checkbox_choices = self.fields["licensing_grounds"].choices
        # Create the 'or' divider between the last choice and I do not know
        last_checkbox_value = checkbox_choices[-1][0]
        last_checkbox_label = checkbox_choices[-1][1]
        checkbox_choices[-1] = Choice(
            value=last_checkbox_value,
            label=last_checkbox_label,
            divider="or",
        )
        checkbox_choices.append(Choice("Unknown grounds", "I do not know"))
        checkbox_choices.append(Choice("None of these", "None of these"))
        self.fields["licensing_grounds"].choices = checkbox_choices
        self.helper.layout = Layout(
            Fieldset(
                get_field_with_label_id("licensing_grounds", field_method=Field.checkboxes, label_id="checkbox"),
                aria_describedby="checkbox",
            )
        )

        if self.legal_advisory:
            self.form_h1_header = (
                "Which of these licensing grounds describes your purpose for providing the "
                "(non-legal advisory) sanctioned services?"
            )

        else:
            if professional_or_business_service := self.request.session.get("ProfessionalOrBusinessServicesView", False):
                if professional_or_business_service.get("professional_or_business_service") == "legal_advisory":
                    self.form_h1_header = (
                        "Which of the licensing grounds describes the purpose of the relevant activity for which "
                        "the legal advice is being given?"
                    )
                    self.fields["licensing_grounds"].label = (
                        "If your client is a non-UK national or business and is also outside the UK "
                        "then UK sanctions do not apply to them. Instead you should select the licensing "
                        "grounds that would apply if UK sanctions did apply to them."
                    )
                    self.fields["licensing_grounds"].help_text = "Select all that apply"

    def clean(self):
        cleaned_data = super().clean()
        if licensing_grounds := cleaned_data.get("licensing_grounds"):
            if ("Unknown grounds" in licensing_grounds or "None of these" in licensing_grounds) and len(licensing_grounds) >= 2:
                # the user has selected "I do not know" or 'None of these' and other grounds, this is an issue.
                # note that the user can select both "I do not know" and "None of these"
                self.add_error(
                    "licensing_grounds",
                    forms.ValidationError(code="invalid", message=self.fields["licensing_grounds"].error_messages["invalid"]),
                )

        return cleaned_data

    def get_licensing_grounds_display(self):
        display = []
        for licensing_ground in self.cleaned_data["licensing_grounds"]:
            display += [dict(self.fields["licensing_grounds"].choices)[licensing_ground]]
        display = ",\n\n".join(display)
        return display


class PurposeOfProvisionForm(BaseModelForm):
    class Meta:
        model = ApplicationServices
        fields = ["purpose_of_provision"]
        labels = {
            "purpose_of_provision": "What is your purpose for providing these services?",
        }
        help_texts = {
            "purpose_of_provision": "Tell us how your reasons for providing these services are consistent with "
            "the purposes of the sanctions and why providing them is both necessary and justified. If you've "
            "selected any licensing considerations (licensing grounds), as laid out in the statutory guidance, "
            "explain how your purpose aligns with those grounds"
        }
        error_messages = {
            "purpose_of_provision": {
                "required": "Select the purpose for providing these services",
            }
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["purpose_of_provision"].required = True
