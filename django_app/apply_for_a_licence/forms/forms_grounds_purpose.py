from apply_for_a_licence import choices
from apply_for_a_licence.models import Licence
from apply_for_a_licence.utils import get_cleaned_data_for_step
from core.crispy_fields import get_field_with_label_id
from core.forms.base_forms import BaseForm, BaseModelForm
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import Field, Fieldset, Layout
from django import forms


class LicensingGroundsForm(BaseForm):
    licensing_grounds = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=choices.LicensingGroundsChoices.choices,
        required=True,
        label="Select all that apply",
        error_messages={
            "invalid": "Select the licensing grounds or select I do not know",
        },
    )

    class Meta:
        model = Licence
        fields = ["licensing_grounds"]

    class Media:
        js = ["apply_for_a_licence/javascript/licensing_grounds.js"]

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        services = self.get_services()
        error_messages = self.fields["licensing_grounds"].error_messages
        self.checkbox_choices = self.fields["licensing_grounds"].choices

        for choice in choices.DecommissionedLicensingGroundsChoices.choices:
            print(choice)
            self.checkbox_choices.remove(
                (
                    choice[0],
                    choice[1],
                )
            )

        # Create the 'or' divider between the last choice and I do not know
        last_checkbox_value = self.checkbox_choices[-1][0]
        last_checkbox_label = self.checkbox_choices[-1][1]
        self.checkbox_choices[-1] = Choice(
            value=last_checkbox_value,
            label=last_checkbox_label,
            divider="or",
        )
        self.checkbox_choices.append(Choice("Unknown grounds", "I do not know"))
        self.checkbox_choices.append(Choice("None of these", "None of these"))

        self.fields["licensing_grounds"].choices = self.checkbox_choices
        self.helper.layout = Layout(
            Fieldset(
                get_field_with_label_id("licensing_grounds", field_method=Field.checkboxes, label_id="checkbox"),
                aria_describedby="checkbox",
            )
        )

        if "legal_advisory" in services:
            self.fields["licensing_grounds"].error_messages = error_messages | {
                "required": "Select which licensing grounds describe the purpose of the relevant activity for which the legal "
                "advice is being given, or select none of these, or select I do not know"
            }
        else:
            self.fields["licensing_grounds"].error_messages = error_messages | {
                "required": "Select which licensing grounds describe your purpose for providing"
                " the sanctioned services, or select none of these, or select I do not know"
            }

    def get_services(self):
        return get_cleaned_data_for_step(self.request, "professional_or_business_services").get(
            "professional_or_business_services", []
        )

    def get_licensing_grounds_display(self):
        display = []
        for licensing_ground in self.cleaned_data["licensing_grounds"]:
            display += [dict(self.fields["licensing_grounds"].choices)[licensing_ground]]
        display = ",\n\n".join(display)
        return display


class LicensingGroundsLegalAdvisoryForm(LicensingGroundsForm):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["licensing_grounds"].error_messages = self.fields["licensing_grounds"].error_messages | {
            "required": "Select which licensing grounds describe your purpose for providing "
            "the sanctioned services (excluding legal advisory), or select none of these, or select I do not know"
        }

        self.fields["licensing_grounds"].choices = self.checkbox_choices


class PurposeOfProvisionForm(BaseModelForm):
    class Meta:
        model = Licence
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
                "required": "Enter details of your purpose for providing the sanctioned services",
            }
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["purpose_of_provision"].required = True
