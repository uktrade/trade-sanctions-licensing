from apply_for_a_licence.choices import TypeOfRelationshipChoices
from apply_for_a_licence.models import Organisation
from core.forms.base_forms import (
    BaseBusinessDetailsForm,
    BaseForm,
    BaseModelForm,
    BaseNonUKBusinessDetailsForm,
    BaseUKBusinessDetailsForm,
)
from crispy_forms_gds.choices import Choice
from crispy_forms_gds.layout import Field, Fieldset, Fluid, Layout, Size
from django import forms
from django.utils.safestring import mark_safe


class WhereIsTheRecipientLocatedForm(BaseModelForm):
    class Meta:
        model = Organisation
        fields = ("where_is_the_address",)
        widgets = {
            "where_is_the_address": forms.RadioSelect,
        }
        labels = {
            "where_is_the_address": "Where is the recipient of the services located?",
        }
        error_messages = {
            "where_is_the_address": {
                "required": "Select if the recipient of the services is located outside the UK or in the UK"
            },
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["where_is_the_address"].choices.pop(0)


class AddAUKRecipientForm(BaseUKBusinessDetailsForm):
    form_h1_header = "About the recipient"
    labels = {
        "name": "Name of recipient",
        "email": "Email address (optional)",
        "website": "Website address (optional)",
        "additional_contact_details": "Additional contact details (optional)",
    }
    help_texts = {
        "name": "This could be a business, an individual or a ship",
    }

    class Meta(BaseUKBusinessDetailsForm.Meta):
        model = Organisation
        fields = (
            "name",
            "website",
            "email",
            "country",
            "address_line_1",
            "address_line_2",
            "town_or_city",
            "county",
            "postcode",
            "additional_contact_details",
        )
        widgets = BaseBusinessDetailsForm.Meta.widgets
        labels = BaseBusinessDetailsForm.Meta.labels
        error_messages = BaseBusinessDetailsForm.Meta.error_messages | {
            "address_line_1": {"required": "Enter address line 1, typically the building and street"},
        }
        help_texts = {
            "additional_contact_details": "This could be a phone number, or details of a jurisdiction instead of a country"
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

        address_layout = Fieldset(
            Field.text("address_line_1", field_width=Fluid.TWO_THIRDS),
            Field.text("address_line_2", field_width=Fluid.TWO_THIRDS),
            Field.text("town_or_city", field_width=Fluid.ONE_HALF),
            Field.text("county", field_width=Fluid.ONE_HALF),
            Field.text("postcode", field_width=Fluid.ONE_THIRD),
            legend="Address",
            legend_size=Size.MEDIUM,
            legend_tag="h2",
        )

        self.helper.layout = Layout(
            Fieldset(
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


class AddANonUKRecipientForm(BaseNonUKBusinessDetailsForm):
    form_h1_header = "About the recipient"
    labels = {
        "name": "Name of recipient",
        "email": "Email address (optional)",
        "website": "Website address (optional)",
        "additional_contact_details": "Additional contact details (optional)",
    }
    help_texts = {
        "name": "This could be a business, an individual or a ship",
    }

    class Meta(BaseNonUKBusinessDetailsForm.Meta):
        model = Organisation
        fields = (
            "name",
            "website",
            "email",
            "country",
            "town_or_city",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "address_line_4",
            "additional_contact_details",
        )
        widgets = BaseBusinessDetailsForm.Meta.widgets
        labels = BaseBusinessDetailsForm.Meta.labels
        error_messages = BaseBusinessDetailsForm.Meta.error_messages | {
            "address_line_1": {"required": "Enter address line 1"},
        }
        help_texts = {
            "additional_contact_details": "This could be a phone number, or details of a jurisdiction instead of a country"
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
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
        self.helper.layout = Layout(
            Fieldset(
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
        self.licence_object: object = kwargs.pop("licence_object", None)
        super().__init__(*args, **kwargs)
        self.helper.legend_size = Size.MEDIUM
        self.helper.legend_tag = None

        if self.request.method == "GET":
            # we never want to pre-fill this form
            self.is_bound = False

    def clean(self):
        cleaned_data = super().clean()
        recipients = Organisation.objects.filter(
            licence=self.licence_object, type_of_relationship=TypeOfRelationshipChoices.recipient.value
        )
        recipient_errors = []
        for x, recipient in enumerate(recipients):
            if recipient.status == "draft":
                recipient_errors.append(f"Recipient {x + 1} must be completed or removed")
        if recipient_errors:
            raise forms.ValidationError(
                mark_safe("<br/>".join(recipient_errors)),
                code="incomplete_recipient",
            )
        return cleaned_data


class RelationshipProviderRecipientForm(BaseModelForm):
    class Meta:
        model = Organisation
        fields = ("relationship_provider",)
        labels = {
            "relationship_provider": "What is the relationship between the provider of the services and the recipient?",
        }
        help_texts = {
            "relationship_provider": "For example, the recipient is a subsidiary of the provider; or there is no relationship",
        }
        error_messages = {
            "relationship_provider": {
                "required": "Enter the relationship between the provider of the services and the recipient"
            },
        }
        widgets = {
            "relationship_provider": forms.Textarea(attrs={"rows": 5}),
        }
