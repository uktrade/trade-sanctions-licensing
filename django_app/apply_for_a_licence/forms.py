from core.forms.base_forms import BaseForm, BaseModelForm
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import Field, Fluid, Layout, Size
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
