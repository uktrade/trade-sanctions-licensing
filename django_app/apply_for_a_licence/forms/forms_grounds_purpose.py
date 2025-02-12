from apply_for_a_licence import choices
from apply_for_a_licence.models import Licence
from core.crispy_fields import get_field_with_label_id
from core.forms.base_forms import BaseModelForm
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import Field, Fieldset, Layout
from django import forms


class BaseLicensingGroundsForm(BaseModelForm):
    field_name: str | None = None

    class Media:
        js = ["apply_for_a_licence/javascript/licensing_grounds.js"]

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        # setting the labels and widgets
        self.fields[self.field_name].label = "Select all that apply"

        self.checkbox_choices = choices.LicensingGroundsChoices.active_choices()
        # Create the 'or' divider between the last choice and I do not know
        last_actual_licensing_ground_value = self.checkbox_choices[-3][0]
        last_actual_licensing_ground_label = self.checkbox_choices[-3][1]
        assert last_actual_licensing_ground_value == choices.LicensingGroundsChoices.food.value
        self.checkbox_choices[-3] = Choice(
            value=last_actual_licensing_ground_value,
            label=last_actual_licensing_ground_label,
            divider="or",
        )
        self.fields[self.field_name].choices = self.checkbox_choices

        if self.instance.professional_or_business_services:
            if choices.ProfessionalOrBusinessServicesChoices.legal_advisory in self.instance.professional_or_business_services:
                self.fields[self.field_name].error_messages = {
                    "required": "Select which licensing grounds describe the purpose of the relevant "
                    "activity for which the legal advice is being given, or select none of these, "
                    "or select I do not know"
                }
            else:
                self.fields[self.field_name].error_messages = {
                    "required": "Select which licensing grounds describe your purpose for providing"
                    " the sanctioned services, or select none of these, or select I do not know"
                }

        self.helper.layout = Layout(
            Fieldset(
                get_field_with_label_id(self.field_name, field_method=Field.checkboxes, label_id="checkbox"),
                aria_describedby="checkbox",
            )
        )


class LicensingGroundsForm(BaseLicensingGroundsForm):
    field_name = "licensing_grounds"

    class Meta:
        model = Licence
        fields = ["licensing_grounds"]
        widgets = {
            "licensing_grounds": forms.CheckboxSelectMultiple,
        }


class LicensingGroundsLegalAdvisoryForm(BaseLicensingGroundsForm):
    field_name = "licensing_grounds_legal_advisory"

    class Meta(LicensingGroundsForm.Meta):
        model = Licence
        fields = ["licensing_grounds_legal_advisory"]
        widgets = {
            "licensing_grounds_legal_advisory": forms.CheckboxSelectMultiple,
        }


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
        kwargs["pk"] = self.instance.pk
