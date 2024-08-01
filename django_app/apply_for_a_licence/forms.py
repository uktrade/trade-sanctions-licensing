import os
from datetime import timedelta
from typing import Any

from core.crispy_fields import HTMLTemplate, get_field_with_label_id
from core.document_storage import TemporaryDocumentStorage
from core.forms.base_forms import BaseBusinessDetailsForm, BaseForm, BaseModelForm
from core.utils import get_mime_type, is_request_ratelimited
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.helper import FormHelper
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
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import escape
from django.utils.timezone import now
from django_chunk_upload_handlers.clam_av import VirusFoundInFileException
from utils.companies_house import (
    get_details_from_companies_house,
    get_formatted_address,
)
from utils.s3 import get_all_session_files

from . import choices
from .exceptions import CompaniesHouse500Error, CompaniesHouseException
from .fields import MultipleFileField
from .models import (
    Applicant,
    ApplicationOrganisation,
    ApplicationServices,
    ApplicationType,
    BaseApplication,
    Document,
    ExistingLicences,
    Ground,
    Individual,
    Organisation,
    Regime,
    Services,
    UserEmailVerification,
)


class StartForm(BaseModelForm):
    class Meta:
        model = ApplicationType
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
            "invalid": "Enter a valid email address",
        },
    )


class YourDetailsForm(BaseModelForm):
    form_h1_header = "Your details"

    class Meta:
        model = Applicant
        fields = ["full_name", "business", "role"]
        labels = {
            "full_name": "Full name",
            "business": "Business you work for",
            "role": "Your role",
        }
        help_texts = {
            "business": "If you're a third-party agent, this is the business that employs you, "
            "not the business needing the licence",
        }
        error_messages = {
            "full_name": {"required": "Enter your full name"},
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.label_size = Size.MEDIUM
        self.helper.layout = Layout(
            Field.text("full_name", field_width=Fluid.TWO_THIRDS),
            Field.text("business", field_width=Fluid.TWO_THIRDS),
            Field.text("role", field_width=Fluid.TWO_THIRDS),
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


class IsTheBusinessRegisteredWithCompaniesHouseForm(BaseModelForm):
    class Meta:
        model = BaseApplication
        fields = ["business_registered_on_companies_house"]
        widgets = {"business_registered_on_companies_house": forms.RadioSelect}
        labels = {
            "business_registered_on_companies_house": "Is the business you want the "
            "licence to cover registered with UK Companies House?"
        }
        error_messages = {
            "business_registered_on_companies_house": {
                "required": "Select yes if the business you want the licence to cover is registered with UK Companies House"
            }
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["business_registered_on_companies_house"].choices.pop(0)


class DoYouKnowTheRegisteredCompanyNumberForm(BaseModelForm):
    hide_optional_label_fields = ["registered_company_number"]

    registered_company_name = forms.CharField(required=False)
    registered_office_address = forms.CharField(required=False)

    class Meta:
        model = Organisation
        fields = ["do_you_know_the_registered_company_number", "registered_company_number"]
        widgets = {"do_you_know_the_registered_company_number": forms.RadioSelect}
        labels = {
            "do_you_know_the_registered_company_number": "Do you know the registered company number?",
            "registered_company_number": "Registered company number",
        }
        error_messages = {
            "do_you_know_the_registered_company_number": {"required": "Select yes if you know the registered company number"},
            "registered_company_number": {
                "required": "Enter the registered company number",
                "invalid": "Number not recognised with Companies House. Enter the correct registered company number. "
                "This is usually an 8-digit number.",
            },
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        # emptying the form if the user has requested to change the details
        if self.request.GET.get("change") == "yes":
            self.is_bound = False
            self.data = {}

        # remove companies house 500 error if it exists
        self.request.session.pop("company_details_500", None)
        self.request.session.modified = True

        # todo - abstract the following logic to apply to all ConditionalRadios forms
        self.helper.legend_tag = "h1"
        self.helper.legend_size = Size.LARGE
        self.helper.label_tag = ""
        self.helper.label_size = None
        self.helper.layout = Layout(
            ConditionalRadios(
                "do_you_know_the_registered_company_number",
                ConditionalQuestion(
                    "Yes",
                    Field.text("registered_company_number", field_width=Fluid.ONE_THIRD),
                ),
                "No",
            )
        )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        # first we check if the request is rate-limited
        if is_request_ratelimited(self.request):
            raise forms.ValidationError(
                "You've tried to enter the registered company number too many times. Try again in 1 minute"
            )

        do_you_know_the_registered_company_number = cleaned_data.get("do_you_know_the_registered_company_number")
        registered_company_number = cleaned_data.get("registered_company_number")
        if do_you_know_the_registered_company_number == "yes":
            if not registered_company_number:
                self.add_error(
                    "registered_company_number",
                    forms.ValidationError(
                        code="required", message=self.Meta.error_messages["registered_company_number"]["required"]
                    ),
                )
                # we don't need to continue if the company number is missing
                return cleaned_data

            try:
                company_details = get_details_from_companies_house(registered_company_number)
                cleaned_data["registered_company_number"] = company_details["company_number"]
                cleaned_data["registered_company_name"] = company_details["company_name"]
                cleaned_data["registered_office_address"] = get_formatted_address(company_details["registered_office_address"])
            except CompaniesHouseException:
                self.add_error(
                    "registered_company_number",
                    forms.ValidationError(
                        code="invalid", message=self.Meta.error_messages["registered_company_number"]["invalid"]
                    ),
                )
            except CompaniesHouse500Error:
                self.request.session["company_details_500"] = True
                self.request.session.modified = True

        return cleaned_data


class ManualCompaniesHouseInputForm(BaseForm):
    manual_companies_house_input = forms.ChoiceField(
        label="Where is the business located?",
        choices=(
            ("in_the_uk", "In the UK"),
            ("outside_the_uk", "Outside the UK"),
        ),
        widget=forms.RadioSelect,
        error_messages={
            "required": "Select if the address of the business you would like the license for is in the UK, or outside the UK"
        },
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Fieldset(
                Field.radios(
                    "manual_companies_house_input",
                    legend_size=Size.MEDIUM,
                )
            )
        )


class WhereIsTheBusinessLocatedForm(BaseForm):
    where_is_the_address = forms.ChoiceField(
        label="Where is the business located?",
        choices=(
            ("in_the_uk", "In the UK"),
            ("outside_the_uk", "Outside the UK"),
        ),
        widget=forms.RadioSelect,
        error_messages={"required": "Select if the business is located in the UK, or outside the UK"},
    )


class AddABusinessForm(BaseBusinessDetailsForm):
    form_h1_header = "Add a business"

    class Meta(BaseBusinessDetailsForm.Meta):
        model = Organisation
        fields = (
            "name",
            "town_or_city",
            "country",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "county",
            "postcode",
        )
        widgets = BaseBusinessDetailsForm.Meta.widgets
        labels = BaseBusinessDetailsForm.Meta.labels
        error_messages = BaseBusinessDetailsForm.Meta.error_messages

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        if self.is_uk_address:
            address_layout = Fieldset(
                Field.text("country", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_1", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_2", field_width=Fluid.ONE_THIRD),
                Field.text("town_or_city", field_width=Fluid.ONE_THIRD),
                Field.text("county", field_width=Fluid.ONE_THIRD),
                Field.text("postcode", field_width=Fluid.ONE_THIRD),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            )
        else:
            address_layout = Fieldset(
                Field.text("town_or_city", field_width=Fluid.ONE_THIRD),
                Field.text("country", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_1", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_2", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_3", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_4", field_width=Fluid.ONE_THIRD),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            )

        self.helper.layout = Layout(
            Fieldset(
                Field.text("name", field_width=Fluid.ONE_HALF),
                legend="Name",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            address_layout,
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

    nationality = forms.CharField(widget=forms.HiddenInput, required=False)

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

    def clean(self):
        cleaned_data = super().clean()
        if self.cleaned_data.get("nationality_and_location", None):
            cleaned_data["nationality"] = dict(self.fields["nationality_and_location"].choices)[
                self.cleaned_data["nationality_and_location"]
            ]
        return cleaned_data


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


class BusinessEmployingIndividualForm(BaseBusinessDetailsForm):
    form_h1_header = "Details of the business employing the individual[s]"

    class Meta(BaseBusinessDetailsForm.Meta):
        model = Organisation
        fields = (
            "name",
            "country",
            "town_or_city",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "county",
            "postcode",
        )
        widgets = BaseBusinessDetailsForm.Meta.widgets
        labels = BaseBusinessDetailsForm.Meta.labels
        error_messages = BaseBusinessDetailsForm.Meta.error_messages

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Fieldset(
                Field.text("name", field_width=Fluid.ONE_HALF),
                legend="Name",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            Fieldset(
                Field.text("country", field_width=Fluid.ONE_THIRD),
                Field.text("town_or_city", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_1", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_2", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_3", field_width=Fluid.ONE_THIRD),
                Field.text("address_line_4", field_width=Fluid.ONE_THIRD),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
        )


class AddYourselfForm(BaseModelForm):
    form_h1_header = "Your details"
    nationality = forms.CharField(widget=forms.HiddenInput, required=False)

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

    def clean(self):
        cleaned_data = super().clean()
        if self.cleaned_data.get("nationality_and_location", None):
            cleaned_data["nationality"] = dict(self.fields["nationality_and_location"].choices)[
                self.cleaned_data["nationality_and_location"]
            ]
        return cleaned_data


class AddYourselfAddressForm(BaseBusinessDetailsForm):
    form_h1_header = "What is your work address?"

    class Meta(BaseBusinessDetailsForm.Meta):
        model = Organisation
        fields = (
            "town_or_city",
            "country",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "county",
            "postcode",
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
            Field.text("postcode", field_width=Fluid.ONE_THIRD),
        )


class TypeOfServiceForm(BaseModelForm):
    class Meta:
        model = Services
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
        sanctions = Regime.objects.values("full_name")
        if professional_or_business_services := self.request.session.get("TypeOfServiceView", False):
            if professional_or_business_services.get("type_of_service", False) == "internet":
                sanctions = Regime.objects.filter(short_name__in=["Russia", "Belarus"]).values("full_name")

        for i, item in enumerate(sanctions):
            checkbox_choices.append(Choice(item["full_name"], item["full_name"]))

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
        model = Services
        fields = ["professional_or_business_service"]

    def get_professional_or_business_service_display(self):
        display = []
        for professional_or_business_service in self.cleaned_data["professional_or_business_service"]:
            display += [dict(self.fields["professional_or_business_service"].choices)[professional_or_business_service]]
        display = ",\n".join(display)
        return display


class ServiceActivitiesForm(BaseModelForm):
    class Meta:
        model = Services
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

        if professional_or_business_services := self.request.session.get("TypeOfServiceView", False):
            if professional_or_business_services.get("type_of_service", False) == "professional_and_business":
                self.fields["service_activities"].help_text = render_to_string(
                    "apply_for_a_licence/form_steps/partials/professional_or_business_services.html"
                )


class WhereIsTheRecipientLocatedForm(BaseForm):
    where_is_the_address = forms.ChoiceField(
        label="Where is the recipient of the services located?",
        choices=(
            ("in_the_uk", "In the UK"),
            ("outside_the_uk", "Outside the UK"),
        ),
        widget=forms.RadioSelect,
        error_messages={"required": "Select if the recipient of the services is located in the UK, or outside the UK"},
    )


class AddARecipientForm(BaseBusinessDetailsForm):
    form_h1_header = "About the recipient"
    labels = {
        "name_of_person": "Name of person (optional)",
        "email": "Email address (optional)",
        "website": "Website address (optional)",
        "additional_contact_details": "Additional contact details (optional)",
    }
    additional_contact_details = forms.CharField(
        widget=forms.Textarea,
        label="Additional contact details",
        required=False,
    )
    help_texts = {
        "name": "If the recipient is a ship, enter the ship's name",
    }

    class Meta(BaseBusinessDetailsForm.Meta):
        model = Organisation
        fields = (
            "name",
            "name_of_person",
            "website",
            "email",
            "town_or_city",
            "country",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "county",
            "postcode",
        )
        widgets = BaseBusinessDetailsForm.Meta.widgets
        labels = BaseBusinessDetailsForm.Meta.labels
        error_messages = BaseBusinessDetailsForm.Meta.error_messages

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        if self.is_uk_address:
            address_layout = Fieldset(
                Field.text("country", field_width=Fluid.ONE_HALF),
                Field.text("address_line_1", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_2", field_width=Fluid.TWO_THIRDS),
                Field.text("town_or_city", field_width=Fluid.ONE_HALF),
                Field.text("county", field_width=Fluid.ONE_HALF),
                Field.text("postcode", field_width=Fluid.ONE_THIRD),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            )

        else:
            address_layout = Fieldset(
                Field.text("country", field_width=Fluid.TWO_THIRDS),
                Field.text("town_or_city", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_1", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_2", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_3", field_width=Fluid.TWO_THIRDS),
                Field.text("address_line_4", field_width=Fluid.TWO_THIRDS),
                legend="Address",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            )
            self.fields["additional_contact_details"].help_text = (
                "This could be a phone number, or details of a jurisdiction instead of a country"
            )

        self.helper.layout = Layout(
            Fieldset(
                Field.text("name_of_person", field_width=Fluid.TWO_THIRDS),
                Field.text("name", field_width=Fluid.TWO_THIRDS),
                Field.text("email", field_width=Fluid.TWO_THIRDS),
                Field.text("website", field_width=Fluid.TWO_THIRDS),
                legend="Name",
                legend_size=Size.MEDIUM,
                legend_tag="h2",
            ),
            address_layout,
            Field.textarea("additional_contact_details", field_width=Fluid.FULL, rows=5, label_tag="h2", label_size=Size.MEDIUM),
        )


class RecipientAddedForm(BaseForm):
    revalidate_on_done = False

    do_you_want_to_add_another_recipient = forms.TypedChoiceField(
        choices=(
            Choice(True, "Yes"),
            Choice(False, "No"),
        ),
        coerce=lambda x: x == "True",
        label="Do you want to add another recipient?",
        error_messages={"required": "Select yes if you want to add another recipient"},
        widget=forms.RadioSelect,
        required=True,
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.legend_size = Size.MEDIUM
        self.helper.legend_tag = None


class RelationshipProviderRecipientForm(BaseModelForm):
    class Meta:
        model = ApplicationOrganisation
        fields = ["relationship"]
        labels = {
            "relationship": "What is the relationship between the provider of the services and the recipient?",
        }
        help_texts = {
            "relationship": "For example, the recipient is a subsidiary of the provider; " "or there is no relationship",
        }
        error_messages = {
            "relationship": {
                "required": "Relationship between the provider of the services and the recipient cannot be left blank"
            },
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["relationship"].required = True
        self.fields["relationship"].widget.attrs = {"rows": 5}


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


class UploadDocumentsForm(BaseForm):
    revalidate_on_done = False
    document = MultipleFileField(
        label="Upload a file",
        help_text="Maximum individual file size 100MB. Maximum number of uploads 10",
        required=False,
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["document"].widget.attrs["class"] = "govuk-file-upload moj-multi-file-upload__input"
        self.fields["document"].widget.attrs["name"] = "document"
        # redefining this to remove the 'Continue' button from the helper
        self.helper = FormHelper()
        self.helper.layout = Layout("document")

    def clean_document(self) -> list[Document]:
        documents = self.cleaned_data.get("document")
        for document in documents:

            # does the document contain a virus?
            try:
                document.readline()
            except VirusFoundInFileException:
                documents.remove(document)
                raise forms.ValidationError(
                    "A virus was found in one of the files you uploaded.",
                )

            # is the document a valid file type?
            mimetype = get_mime_type(document.file)
            valid_mimetype = mimetype in [
                # word documents
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
                # spreadsheets
                "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                # powerpoints
                "application/vnd.ms-powerpoint",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                # pdf
                "application/pdf",
                # other
                "text/plain",
                "text/csv",
                "application/zip",
                "text/html",
                # images
                "image/jpeg",
                "image/png",
            ]

            _, file_extension = os.path.splitext(document.name)
            valid_extension = file_extension in [
                # word documents
                ".doc",
                ".docx",
                ".odt",
                ".fodt",
                # spreadsheets
                ".xls",
                ".xlsx",
                ".ods",
                ".fods",
                # powerpoints
                ".ppt",
                ".pptx",
                ".odp",
                ".fodp",
                # pdf
                ".pdf",
                # other
                ".txt",
                ".csv",
                ".zip",
                ".html",
                # images
                ".jpeg",
                ".jpg",
                ".png",
            ]

            if not valid_mimetype or not valid_extension:
                raise forms.ValidationError(
                    f"{escape(document.name)} cannot be uploaded, it is not a valid file type", code="invalid_file_type"
                )

            # has the user already uploaded 10 files?
            if session_files := get_all_session_files(TemporaryDocumentStorage(), self.request.session):
                if len(session_files) + 1 > 10:
                    raise forms.ValidationError("You can only select up to 10 files at the same time", code="too_many")

            # is the document too large?
            if document.size > 104857600:
                raise forms.ValidationError(f"{document.name} must be smaller than 100 MB", code="too_large")

        return documents
