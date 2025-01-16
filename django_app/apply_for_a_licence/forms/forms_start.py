from datetime import timedelta

from apply_for_a_licence import choices
from apply_for_a_licence.models import Licence, UserEmailVerification
from core.crispy_fields import HTMLTemplate
from core.forms.base_forms import BaseForm, BaseModelForm
from core.utils import is_request_ratelimited
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import Field, Fluid, Layout, Size
from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.timezone import now


class SubmitterReferenceForm(BaseModelForm):
    class Meta:
        model = Licence
        fields = ["submitter_reference"]
        labels = {"submitter_reference": "Your application name"}
        help_texts = {
            "submitter_reference": "This is for you to keep track of your application. It will not be submitted.",
        }
        error_messages = {"submitter_reference": {"required": "Enter the name of the application"}}

    form_h1_header = "Give your application a name"
    bold_labels = False


class StartForm(BaseModelForm):
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


class ThirdPartyForm(BaseForm):
    are_you_applying_on_behalf_of_someone_else = forms.TypedChoiceField(
        choices=choices.YES_NO_CHOICES,
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
            "invalid": "Enter an email in the correct format, for example name@example.com",
        },
        help_text="We need to send you an email to verify your email address.",
    )


class YourDetailsForm(BaseModelForm):
    form_h1_header = "Your details"

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


class EmailVerifyForm(BaseForm):
    bold_labels = False
    form_h1_header = "We've sent you an email"
    revalidate_on_done = False

    email_verification_code = forms.CharField(
        label="Enter the 6 digit security code",
        error_messages={
            "required": "Enter the 6 digit security code we sent to your email",
            "expired": "The code you entered is no longer valid. Please verify your email again",
            "invalid": "Code is incorrect. Enter the 6 digit security code we sent to your email",
        },
        widget=forms.TextInput(attrs={"style": "max-width: 5em"}),
    )

    def clean_email_verification_code(self) -> str:
        # first we check if the request is rate-limited
        if is_request_ratelimited(self.request):
            raise forms.ValidationError("You've tried to verify your email too many times. Try again in 1 minute")

        email_verification_code = self.cleaned_data["email_verification_code"]
        email_verification_code = email_verification_code.replace(" ", "")

        verify_timeout_seconds = settings.EMAIL_VERIFY_TIMEOUT_SECONDS

        verification_objects = UserEmailVerification.objects.filter(
            user_session=self.request.session.session_key  # type: ignore[attr-defined]
        ).latest("date_created")

        verify_code = verification_objects.email_verification_code
        if email_verification_code != verify_code:
            raise forms.ValidationError("Code is incorrect. Enter the 6 digit security code we sent to your email")

        # check if the user has submitted the verify code within the specified timeframe
        allowed_lapse = verification_objects.date_created + timedelta(seconds=verify_timeout_seconds)
        if allowed_lapse < now():
            time_code_sent = verification_objects.date_created

            # 15 minutes ago, show a ‘code has expired’ error message and send the user a new code
            # 2 hours ago, show an ‘incorrect security code’ message, even if the code was correct
            if time_code_sent > (now() - timedelta(hours=2)):
                raise forms.ValidationError(self.fields["email_verification_code"].error_messages["expired"], code="expired")
            else:
                raise forms.ValidationError(self.fields["email_verification_code"].error_messages["invalid"], code="invalid")

        verification_objects.verified = True
        verification_objects.save()
        return email_verification_code

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.request = kwargs.pop("request") if "request" in kwargs else None
        request_verify_code = reverse_lazy("request_verify_code")
        self.helper["email_verification_code"].wrap(
            Field,
            HTMLTemplate(
                "apply_for_a_licence/form_steps/partials/not_received_code_help_text.html",
                {"request_verify_code": request_verify_code},
            ),
        )
