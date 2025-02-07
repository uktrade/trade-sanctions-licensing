from apply_for_a_licence import choices
from apply_for_a_licence.models import Licence
from core.crispy_fields import HTMLTemplate
from core.forms.base_forms import BaseModelForm
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import HTML, Field, Fluid, Layout, Size
from django import forms


class SubmitterReferenceForm(BaseModelForm):
    class Meta:
        model = Licence
        fields = ["submitter_reference"]
        labels = {"submitter_reference": "Your application name"}
        error_messages = {"submitter_reference": {"required": "Enter the name of the application"}}

    form_h1_header = "Give your application a name"
    bold_labels = False
    save_and_return = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            HTML("<p class='govuk-body'>This is for you to keep track of your application. It will not be submitted.</p>"),
            Field.text("submitter_reference", field_width=Fluid.TWO_THIRDS),
        )

    def save(self, commit=True) -> Licence:
        instance = super().save(commit=False)
        instance.user = self.request.user
        instance.save()
        self.request.session["licence_id"] = instance.id
        return instance


class StartForm(BaseModelForm):
    save_and_return = True

    class Meta:
        model = Licence
        fields = ["who_do_you_want_the_licence_to_cover"]
        labels = {"who_do_you_want_the_licence_to_cover": "Who do you want the licence to cover?"}
        widgets = {
            "who_do_you_want_the_licence_to_cover": forms.RadioSelect,
        }
        error_messages = {"who_do_you_want_the_licence_to_cover": {"required": "Select who you want the licence to cover"}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        CHOICES = (
            Choice(
                choices.WhoDoYouWantTheLicenceToCoverChoices.business.value,
                choices.WhoDoYouWantTheLicenceToCoverChoices.business.label,
                hint="The licence will cover all employees, members, partners, consultants, contractors, officers and directors",
            ),
            Choice(
                choices.WhoDoYouWantTheLicenceToCoverChoices.individual.value,
                choices.WhoDoYouWantTheLicenceToCoverChoices.individual.label,
                hint="If your business has no UK nexus it cannot be licenced, but any employees or consultants with a UK nexus "
                "must be licenced before they can provide sanctioned services for you",
            ),
            Choice(
                choices.WhoDoYouWantTheLicenceToCoverChoices.myself.value,
                choices.WhoDoYouWantTheLicenceToCoverChoices.myself.label,
                hint="Apply for a licence for yourself if you’re a sole trader or cannot be covered by a business licence",
            ),
        )
        self.fields["who_do_you_want_the_licence_to_cover"].choices = CHOICES
        self.helper.layout = Layout(
            *self.fields, HTMLTemplate(html_template_path="apply_for_a_licence/form_steps/partials/uk_nexus_details.html")
        )


class ThirdPartyForm(BaseModelForm):
    save_and_return = True
    is_third_party = forms.TypedChoiceField(
        choices=choices.YES_NO_CHOICES,
        coerce=lambda x: x == "True",
        widget=forms.RadioSelect,
        label="Are you a third-party applying on behalf of a business you represent?",
        error_messages={
            "required": "Select yes if you're an external third party applying on behalf of a business you represent"
        },
        help_text="Such as external legal counsel or an external agent",
    )

    class Meta:
        model = Licence
        fields = ["is_third_party"]


class YourDetailsForm(BaseModelForm):
    form_h1_header = "Your details"
    save_and_return = True

    class Meta:
        model = Licence
        fields = ["applicant_full_name", "applicant_business", "applicant_role"]
        labels = {
            "applicant_full_name": "Full name",
            "applicant_business": "Business you work for",
            "applicant_role": "Your role",
        }
        help_texts = {
            "applicant_business": "If you're a third-party agent, this is the business that employs you, "
            "not the business needing the licence",
        }
        error_messages = {
            "applicant_full_name": {"required": "Enter your full name"},
            "applicant_business": {"required": "Enter the business you work for"},
            "applicant_role": {"required": "Enter your role"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout(
            Field.text("applicant_full_name", field_width=Fluid.TWO_THIRDS),
            Field.text("applicant_business", field_width=Fluid.TWO_THIRDS),
            Field.text("applicant_role", field_width=Fluid.TWO_THIRDS),
        )
