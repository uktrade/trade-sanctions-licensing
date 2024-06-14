from crispy_forms_gds.choices import Choice
from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Layout, Size, Submit, Field
from django import forms

from .base_forms import BaseForm


class CookiesConsentForm(BaseForm):
    do_you_want_to_accept_analytics_cookies = forms.TypedChoiceField(
        choices=(
            Choice(True, "Yes"),
            Choice(False, "No"),
        ),
        coerce=lambda x: x == "True",
        widget=forms.RadioSelect,
        label="Do you want to accept analytics cookies",
        required=True,
    )

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("save cookie settings", "Save cookie settings", css_class="govuk-button"))
        self.helper.layout = Layout(
            Field.radios("do_you_want_to_accept_analytics_cookies", legend_size=Size.MEDIUM, legend_tag="h2",
                         inline=False)
        )
        # Allows us to display to the user their previously selected cookies choice in the radios
        kwargs_initial = kwargs.get("initial")
        if kwargs_initial:
            self.fields["do_you_want_to_accept_analytics_cookies"].initial = str(kwargs_initial["accept_cookies"])


class HideCookiesForm(BaseForm):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("hide cookie message", "Hide cookie message", css_class="govuk-button"))
