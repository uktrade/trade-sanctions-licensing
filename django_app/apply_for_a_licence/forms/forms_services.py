from apply_for_a_licence import choices
from apply_for_a_licence.choices import TypeOfServicesChoices
from apply_for_a_licence.models import Licence
from core.crispy_fields import get_field_with_label_id
from core.forms.base_forms import BaseForm, BaseModelForm
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import Field, Fieldset, Layout
from django import forms
from django.template.loader import render_to_string
from sanctions_regimes.licensing import active_regimes


class TypeOfServiceForm(BaseModelForm):
    class Meta:
        model = Licence
        fields = ["type_of_service"]
        widgets = {"type_of_service": forms.RadioSelect}
        error_messages = {
            "type_of_service": {
                "required": "Select the type of service you want to provide",
            }
        }
        labels = {
            "type_of_service": "What type of service do you want to provide?",
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["type_of_service"].choices.pop(0)


class WhichSanctionsRegimeForm(BaseForm):
    form_h1_header = "Which sanctions regime is the licence for?"

    which_sanctions_regime = forms.MultipleChoiceField(
        help_text=("Select all that apply"),
        widget=forms.CheckboxSelectMultiple,
        choices=(()),
        required=True,
        error_messages={
            "required": "Select the sanctions regime the licence is for",
        },
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        checkbox_choices = []

        sanctions = active_regimes

        for item in sanctions:
            checkbox_choices.append(Choice(item["name"], item["name"]))

        self.fields["which_sanctions_regime"].choices = checkbox_choices
        self.fields["which_sanctions_regime"].label = False
        self.helper.label_size = None
        self.helper.label_tag = None
        self.helper.layout = Layout(
            Fieldset(
                get_field_with_label_id("which_sanctions_regime", field_method=Field.checkboxes, label_id="checkbox"),
                aria_describedby="checkbox",
            )
        )

    def get_which_sanctions_regime_display(self):
        display = "\n\n".join(self.cleaned_data["which_sanctions_regime"])
        return display


class ProfessionalOrBusinessServicesForm(BaseModelForm):
    form_h1_header = "What are the professional or business services you want to provide?"
    professional_or_business_service = forms.MultipleChoiceField(
        label=False,
        help_text=("Select all that apply"),
        widget=forms.CheckboxSelectMultiple,
        choices=choices.ProfessionalOrBusinessServicesChoices.choices,
        required=True,
        error_messages={
            "required": "Select the professional or business services the licence is for",
        },
    )

    class Meta:
        model = Licence
        fields = ["professional_or_business_service"]

    def get_professional_or_business_service_display(self):
        display = []
        for professional_or_business_service in self.cleaned_data["professional_or_business_service"]:
            display += [dict(self.fields["professional_or_business_service"].choices)[professional_or_business_service]]
        display = ",\n".join(display)
        return display


class ServiceActivitiesForm(BaseModelForm):
    class Meta:
        model = Licence
        fields = ["service_activities"]
        labels = {
            "service_activities": "Describe the specific activities within the services you want to provide",
        }
        help_texts = {
            "service_activities": "Tell us about the services you want to provide. You will need to show how they "
            "match to the specific meaning of services in the sanctions regime that applies to your intended activity",
        }
        error_messages = {
            "service_activities": {"required": "Enter the specific activities within the services you want to provide"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["service_activities"].widget.attrs = {"rows": 5}

        if professional_or_business_services := (self.request.session.get("type_of_service", {})):
            if (
                professional_or_business_services.get("type_of_service", False)
                == TypeOfServicesChoices.professional_and_business.value
            ):
                self.fields["service_activities"].help_text = render_to_string(
                    "apply_for_a_licence/form_steps/partials/professional_or_business_services.html"
                )
