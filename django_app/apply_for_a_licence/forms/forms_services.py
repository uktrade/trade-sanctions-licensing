from apply_for_a_licence import choices
from apply_for_a_licence.choices import TypeOfServicesChoices
from apply_for_a_licence.models import Licence
from apply_for_a_licence.utils import get_active_regimes
from core.crispy_fields import get_field_with_label_id
from core.forms.base_forms import BaseModelForm
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import Field, Fieldset, Layout
from django import forms
from django.template.loader import render_to_string


class TypeOfServiceForm(BaseModelForm):
    save_and_return = True

    class Meta:
        model = Licence
        fields = ["type_of_service"]
        widgets = {"type_of_service": forms.RadioSelect}
        error_messages = {
            "type_of_service": {
                "required": "Select which type of services you want to provide",
            }
        }
        labels = {
            "type_of_service": "What type of services do you want to provide?",
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["type_of_service"].choices.pop(0)

    def save(self, commit: bool = True):
        licence = super().save(commit=False)

        if self.has_field_changed("type_of_service"):
            # if the type of service has changed, we want to clear the licence data for the next steps
            old_value = self.initial["type_of_service"]

            # we want to clear the service_activities and the purpose_of_provision if the type of service has changed
            licence.service_activities = None
            licence.purpose_of_provision = None

            if old_value == TypeOfServicesChoices.professional_and_business.value:
                # changed from Professional or Business Services to other service
                licence.professional_or_business_services = []
                licence.licensing_grounds = []

            if old_value == TypeOfServicesChoices.interception_or_monitoring.value:
                # changed from Interception or Monitoring to other service
                licence.regimes = None

        licence.save()
        return licence


class WhichSanctionsRegimeForm(BaseModelForm):
    save_and_return = True

    class Meta:
        model = Licence
        fields = ["regimes"]
        help_texts = {
            "regimes": "Select all that apply",
        }
        widgets = {
            "regimes": forms.CheckboxSelectMultiple,
        }
        error_messages = {
            "regimes": {
                "required": "Select which sanctions regime the licence is for",
            }
        }

    form_h1_header = "Which sanctions regime is the licence for?"

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        checkbox_choices = []

        sanctions = get_active_regimes()

        for item in sanctions:
            checkbox_choices.append(Choice(item["name"], item["name"]))

        self.fields["regimes"].choices = checkbox_choices
        self.fields["regimes"].label = False
        self.helper.label_size = None
        self.helper.label_tag = None
        self.helper.layout = Layout(
            Fieldset(
                get_field_with_label_id("regimes", field_method=Field.checkboxes, label_id="checkbox"),
                aria_describedby="checkbox",
            )
        )


class ProfessionalOrBusinessServicesForm(BaseModelForm):
    save_and_return = True

    professional_or_business_services = forms.MultipleChoiceField(
        label=False,
        help_text=("Select all that apply"),
        widget=forms.CheckboxSelectMultiple,
        choices=choices.ProfessionalOrBusinessServicesChoices.choices,
        required=True,
        error_messages={
            "required": "Select the professional or business services you want to provide",
        },
    )

    class Meta:
        model = Licence
        fields = ["professional_or_business_services"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                Field.checkboxes(
                    "professional_or_business_services",
                    label="What are the professional or business services you want to provide?",
                ),
                legend="What are the professional or business services you want to provide?",
                legend_size="l",
                legend_tag="h1",
            )
        )


class ServiceActivitiesForm(BaseModelForm):
    save_and_return = True

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
            "service_activities": {"required": "Enter details about the services you want to provide"},
        }
        widgets = {
            "service_activities": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        if self.instance.type_of_service == TypeOfServicesChoices.professional_and_business.value:
            self.fields["service_activities"].help_text = render_to_string(
                "apply_for_a_licence/form_steps/partials/professional_or_business_services.html"
            )
