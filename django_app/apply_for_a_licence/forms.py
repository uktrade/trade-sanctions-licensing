from datetime import timedelta
from typing import Any

from core.crispy_fields import HTMLTemplate
from core.forms.base_forms import BaseBusinessDetailsForm, BaseForm, BaseModelForm
from core.utils import is_request_ratelimited
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import (
    ConditionalQuestion,
    ConditionalRadios,
    Field,
    Fieldset,
    Fluid,
    Layout,
    Size,
)
from django import forms
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.timezone import now

from . import choices
from .choices import YES_NO_CHOICES
from .models import Business, Individual, Licence, UserEmailVerification


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


class YourDetailsForm(BaseModelForm):
    form_h1_header = "Your details"

    class Meta:
        model = Licence
        fields = ["your_details_full_name", "your_details_name_of_business_you_work_for", "your_details_role"]
        labels = {
            "your_details_full_name": "Full name",
            "your_details_name_of_business_you_work_for": "Business you work for",
            "your_details_role": "Your role",
        }
        help_texts = {
            "your_details_name_of_business_you_work_for": "If you're a third-party agent, this is the business that employs you, "
            "not the business needing the licence",
        }
        error_messages = {
            "your_details_full_name": {"required": "Enter your full name"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout(
            Field.text("your_details_full_name", field_width=Fluid.TWO_THIRDS),
            Field.text("your_details_name_of_business_you_work_for", field_width=Fluid.TWO_THIRDS),
            Field.text("your_details_role", field_width=Fluid.TWO_THIRDS),
        )


class EmailVerifyForm(BaseForm):
    bold_labels = False
    form_h1_header = "We've sent you an email"
    revalidate_on_done = False

    email_verification_code = forms.CharField(
        label="Enter the 6 digit security code",
        error_messages={"required": "Enter the 6 digit security code we sent to your email"},
    )

    def clean_email_verification_code(self) -> str:
        # first we check if the request is rate-limited
        if is_request_ratelimited(self.request):
            raise forms.ValidationError("You've tried to verify your email too many times. Try again in 1 minute")

        email_verification_code = self.cleaned_data["email_verification_code"]
        email_verification_code = email_verification_code.replace(" ", "")

        verify_timeout_seconds = settings.EMAIL_VERIFY_TIMEOUT_SECONDS

        verification_objects = UserEmailVerification.objects.filter(user_session=self.request.session.session_key).latest(
            "date_created"
        )
        verify_code = verification_objects.email_verification_code
        if email_verification_code != verify_code:
            raise forms.ValidationError("Code is incorrect. Enter the 6 digit security code we sent to your email")

        # check if the user has submitted the verify code within the specified timeframe
        allowed_lapse = verification_objects.date_created + timedelta(seconds=verify_timeout_seconds)
        if allowed_lapse < now():
            raise forms.ValidationError("The code you entered is no longer valid. Please verify your email again")

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


class SummaryForm(BaseForm):
    pass


class PreviousLicenceForm(BaseModelForm):
    hide_optional_label_fields = ["previous_licences"]

    class Meta:
        model = Licence
        fields = ("held_previous_licence", "previous_licences")
        labels = {
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
        self.request = kwargs.pop("request") if "request" in kwargs else None
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
        self.held_previous_licence_label = (
            "Have any of the businesses you've added held a licence before to provide sanctioned services?"
        )
        if start_view := self.request.session.get("StartView", False):
            if start_view.get("who_do_you_want_the_licence_to_cover") == "myself":
                self.held_previous_licence_label = (
                    "Have you, or has anyone else you've added, held a licence before to provide sanctioned services?"
                )
            elif start_view.get("who_do_you_want_the_licence_to_cover") == "individual":
                self.held_previous_licence_label = (
                    "Have any of the individuals you've added held a licence before to provide sanctioned services?"
                )
        self.fields["held_previous_licence"].label = self.held_previous_licence_label

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if cleaned_data.get("held_previous_licence") == "yes" and not cleaned_data["previous_licences"]:
            self.add_error("previous_licences", self.Meta.error_messages["previous_licences"]["required"])
        return cleaned_data


class AddABusinessForm(BaseBusinessDetailsForm):
    form_h1_header = "Add a business"
    labels = {
        "name": "Name of business",
    }

    name = forms.CharField()

    class Meta(BaseBusinessDetailsForm.Meta):
        model = Business
        fields = (
            "town_or_city",
            "country",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "county",
            "postal_code",
        )
        widgets = BaseBusinessDetailsForm.Meta.widgets
        labels = BaseBusinessDetailsForm.Meta.labels
        error_messages = BaseBusinessDetailsForm.Meta.error_messages

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        # all fields on this form are optional. Except if it's a non-UK user, then we need the country at least
        for _, field in self.fields.items():
            field.required = False

        if not self.is_uk_address:
            self.fields["country"].required = True

        self.helper.layout = Layout(
            Fieldset(
                Field.text("name", field_width=Fluid.ONE_HALF),
                legend="Name",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Fieldset(
                Field.text("town_or_city", field_width=Fluid.ONE_THIRD),
                Field.text("country", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_1", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_2", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_3", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_4", field_width=Fluid.ONE_THIRD),
                Field.text("county", field_width=Fluid.ONE_THIRD),
                Field.text("postal_code", field_width=Fluid.ONE_THIRD),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
        )


class BusinessAddedForm(BaseForm):
    revalidate_on_done = False

    do_you_want_to_add_another_business = forms.TypedChoiceField(
        choices=(
            Choice(True, "Yes"),
            Choice(False, "No"),
        ),
        coerce=lambda x: x == "True",
        label="Do you want to add another business?",
        error_messages={"required": "Select yes if you want to add another business"},
        widget=forms.RadioSelect,
        required=True,
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.legend_size = Size.MEDIUM
        self.helper.legend_tag = None


class AddAnIndividualForm(BaseModelForm):
    form_h1_header = "Add an individual"

    class Meta:
        model = Individual
        fields = [
            "first_name",
            "last_name",
            "nationality_and_location",
        ]
        widgets = {"first_name": forms.TextInput, "last_name": forms.TextInput, "nationality_and_location": forms.RadioSelect}
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "nationality_and_location": "What is the individual's nationality and location?",
        }
        help_texts = {"nationality_and_location": "Hint text"}
        error_messages = {"first_name": {"required": "Enter your first name"}, "last_name": {"required": "Enter your last name"}}

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["nationality_and_location"].choices.pop(0)
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout(
            Field.text("first_name", field_width=Fluid.ONE_THIRD),
            Field.text("last_name", field_width=Fluid.ONE_THIRD),
            Field.radios("nationality_and_location", legend_size=Size.MEDIUM, legend_tag="h2"),
        )


class IndividualAddedForm(BaseForm):
    revalidate_on_done = False

    do_you_want_to_add_another_individual = forms.TypedChoiceField(
        choices=(
            Choice(True, "Yes"),
            Choice(False, "No"),
        ),
        coerce=lambda x: x == "True",
        label="Do you want to add another individual?",
        error_messages={"required": "Select yes if you want to add another individual"},
        widget=forms.RadioSelect,
        required=True,
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.legend_size = Size.MEDIUM
        self.helper.legend_tag = None


class AddYourselfForm(BaseModelForm):
    form_h1_header = "Your details"

    class Meta:
        model = Individual
        fields = [
            "first_name",
            "last_name",
            "nationality_and_location",
        ]
        widgets = {"first_name": forms.TextInput, "last_name": forms.TextInput, "nationality_and_location": forms.RadioSelect}
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "nationality_and_location": "What is your nationality and location?",
        }
        help_texts = {"nationality_and_location": "Hint text"}
        error_messages = {"first_name": {"required": "Enter your first name"}, "last_name": {"required": "Enter your last name"}}

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["nationality_and_location"].choices.pop(0)
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout(
            Field.text("first_name", field_width=Fluid.ONE_THIRD),
            Field.text("last_name", field_width=Fluid.ONE_THIRD),
            Field.radios("nationality_and_location", legend_size=Size.MEDIUM, legend_tag="h2"),
        )


class AddYourselfAddressForm(BaseBusinessDetailsForm):
    form_h1_header = "What is your work address?"

    class Meta(BaseBusinessDetailsForm.Meta):
        model = Business
        fields = (
            "town_or_city",
            "country",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "county",
            "postal_code",
        )
        widgets = BaseBusinessDetailsForm.Meta.widgets
        labels = BaseBusinessDetailsForm.Meta.labels
        error_messages = BaseBusinessDetailsForm.Meta.error_messages

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        # all fields on this form are optional. Except if it's a non-UK user, then we need the country at least
        for _, field in self.fields.items():
            field.required = False

        if not self.is_uk_address:
            self.fields["country"].required = True

        self.helper.layout = Layout(
            Field.text("town_or_city", field_width=Fluid.ONE_THIRD),
            Field.text("country", field_width=Fluid.ONE_THIRD),
            Field.text("address_line_1", field_width=Fluid.ONE_THIRD),
            Field.text("address_line_2", field_width=Fluid.ONE_THIRD),
            Field.text("address_line_3", field_width=Fluid.ONE_THIRD),
            Field.text("address_line_4", field_width=Fluid.ONE_THIRD),
            Field.text("county", field_width=Fluid.ONE_THIRD),
            Field.text("postal_code", field_width=Fluid.ONE_THIRD),
        )
