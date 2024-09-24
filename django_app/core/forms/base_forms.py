import re
from typing import Any, Dict

from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Layout, Size, Submit
from django import forms
from django.http import HttpRequest
from utils.companies_house import get_formatted_address


class EmptyForm(forms.Form):
    pass


class BaseForm(forms.Form):
    bold_labels = True
    form_h1_header = None
    single_question_form = False
    show_back_button = True
    # fields that you don't want to display (optional) next to the label if they're not required
    hide_optional_label_fields = []
    # if we're using a BaseForm and NOT a BaseModelForm, then we need to implement our own labels dictionary to set the labels
    labels = {}
    # same for help_texts
    help_texts = {}
    # do we want this form to be revalidated when the user clicks Done
    revalidate_on_done = True
    # the submit button text
    submit_button_text = "Continue"

    class Media:
        css = {
            "all": ["form.css"],
        }

    def __init__(self, *args: object, **kwargs: Dict[str, Any]) -> None:
        self.request: HttpRequest | None = kwargs.pop("request", None)
        self.form_h1_header = kwargs.pop("form_h1_header", self.form_h1_header)
        self.should_be_bound: bool = kwargs.pop("should_be_bound", False)
        super().__init__(*args, **kwargs)

        if len(self.fields) == 1:
            self.single_question_form = True

        for field_name, label in self.labels.items():
            self.fields[field_name].label = label

        for field_name, help_text in self.help_texts.items():
            self.fields[field_name].help_text = help_text

        self.helper = FormHelper()
        self.helper.add_input(Submit("continue", self.submit_button_text, css_class="btn-primary"))

        if self.single_question_form and not self.form_h1_header:
            self.helper.label_tag = "h1"
            self.helper.legend_tag = "h1"
            self.helper.legend_size = Size.LARGE

        if self.bold_labels:
            self.helper.label_size = Size.LARGE

        self.helper.layout = Layout(*self.fields)

        # clearing the form data if 'change' is passed as a query parameter, and it's a GET request
        if self.request and self.request.method == "GET" and self.request.GET.get("change"):
            self.is_bound = False


class BaseModelForm(BaseForm, forms.ModelForm):
    pass


class BaseBusinessDetailsForm(BaseModelForm):
    """A base form for capturing business details. Such as the AddABusiness Form"""

    class Meta:
        widgets = {
            "name": forms.TextInput,
            "website": forms.TextInput,
            "country": forms.Select,
            "address_line_1": forms.TextInput,
            "address_line_2": forms.TextInput,
            "address_line_3": forms.TextInput,
            "address_line_4": forms.TextInput,
            "town_or_city": forms.TextInput,
            "county": forms.TextInput,
            "postcode": forms.TextInput,
        }
        labels = {
            "name": "Name of business",
            "country": "Country",
            "address_line_1": "Address line 1",
            "address_line_2": "Address line 2 (optional)",
            "address_line_3": "Address line 3 (optional)",
            "address_line_4": "Address line 4 (optional)",
            "town_or_city": "Town or city",
            "county": "County (optional)",
            "postcode": "Postcode",
        }
        error_messages = {
            "name": {"required": "Enter the name of the business"},
            "address_line_1": {"required": "Enter address line 1, such as the building and street"},
            "town_or_city": {"required": "Enter town or city"},
            "postcode": {"required": "Enter postcode", "invalid": "Enter a full UK postcode"},
            "country": {"required": "Select country"},
        }

    readable_address = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.label_size = None
        self.fields["town_or_city"].required = True
        self.fields["address_line_1"].required = True

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        cleaned_data["readable_address"] = get_formatted_address(cleaned_data)
        return cleaned_data


class BaseUKBusinessDetailsForm(BaseBusinessDetailsForm):
    """A base form for capturing UK business details. Such as the AddAUKBusiness Form"""

    class Meta(BaseBusinessDetailsForm.Meta):
        widgets = BaseBusinessDetailsForm.Meta.widgets
        labels = BaseBusinessDetailsForm.Meta.labels
        error_messages = BaseBusinessDetailsForm.Meta.error_messages
        fields = (
            "name",
            "website",
            "email",
            "town_or_city",
            "country",
            "address_line_1",
            "address_line_2",
            "county",
            "postcode",
        )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["postcode"].required = True
        self.fields["country"].initial = "GB"
        self.fields["country"].widget = forms.HiddenInput()

        self.helper.label_size = None

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        cleaned_data["country"] = "GB"
        cleaned_data["url_location"] = "in-uk"
        return cleaned_data

    def clean_postcode(self) -> dict[str, Any]:
        postcode = self.cleaned_data.get("postcode")
        if postcode:
            # we want to validate a UK postcode
            pattern = re.compile(r"^[A-Za-z]{1,2}\d[A-Za-z\d]? ?\d[A-Za-z]{2}$")
            if not pattern.match(postcode):
                raise forms.ValidationError(code="invalid", message=self.fields["postcode"].error_messages["invalid"])
        return postcode


class BaseNonUKBusinessDetailsForm(BaseBusinessDetailsForm):
    """A base form for capturing non-UK business details. Such as the AddANonUKBusiness Form"""

    class Meta(BaseBusinessDetailsForm.Meta):
        widgets = BaseBusinessDetailsForm.Meta.widgets
        labels = BaseBusinessDetailsForm.Meta.labels
        error_messages = BaseBusinessDetailsForm.Meta.error_messages
        fields = (
            "name",
            "website",
            "email",
            "town_or_city",
            "country",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
        )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        self.fields["country"].required = True
        self.fields["country"].empty_label = "Select country"

        self.helper.label_size = None

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        cleaned_data["url_location"] = "outside-uk"
        return cleaned_data


class GenericForm(BaseForm):
    """Generic form when we're using a FormView which doesn't actually require a form"""

    pass
