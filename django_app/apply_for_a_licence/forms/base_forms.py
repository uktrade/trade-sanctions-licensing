from core.forms.base_forms import BaseForm
from crispy_forms_gds.layout import Size
from django import forms
from django.utils.safestring import mark_safe


class BaseEntityAddedForm(BaseForm):
    revalidate_on_done = False
    allow_zero_entities = False

    @property
    def entity_name(self) -> str:
        raise NotImplementedError("You need to implement the entity_name property")

    @property
    def entities(self):
        raise NotImplementedError("You need to implement the entities property")

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.helper.legend_size = Size.MEDIUM
        self.helper.legend_tag = None

        if self.request.method == "GET":
            self.is_bound = False

    def clean(self):
        cleaned_data = super().clean()
        entity_errors = []

        for x, entity in enumerate(self.entities):
            if entity.status == "draft":
                entity_errors.append(x + 1)

        if len(entity_errors) > 0:
            if f"do_you_want_to_add_another_{self.entity_name}" not in cleaned_data:
                del self.errors[f"do_you_want_to_add_another_{self.entity_name}"]
            if len(self.entities) == 1 and not self.allow_zero_entities:
                if cleaned_data.get(f"do_you_want_to_add_another_{self.entity_name}", False):
                    error_message = (
                        f"You cannot add another {self.entity_name} until {self.entity_name.capitalize()} 1 "
                        f"details are completed. Select 'change' and complete the details"
                    )
                else:
                    error_message = (
                        f"{self.entity_name.capitalize()} 1 details have not yet been completed. "
                        f"Select 'change' and complete the details"
                    )
                raise forms.ValidationError(
                    error_message,
                    code=f"incomplete_{self.entity_name}",
                )
            else:
                error_messages = []
                for entity in entity_errors:
                    if cleaned_data.get(f"do_you_want_to_add_another_{self.entity_name}", False):
                        error_messages.append(
                            f"You cannot add another {self.entity_name} until {self.entity_name.capitalize()} {entity} "
                            f"details are either completed or the {self.entity_name} is removed. Select 'change' and "
                            f"complete the details, or select 'Remove' to remove {self.entity_name.capitalize()} {entity}"
                        )
                    else:
                        error_messages.append(
                            f"{self.entity_name.capitalize()} {entity} details have not yet been completed. Select "
                            f"'change' and complete the details, or select 'Remove' to "
                            f"remove {self.entity_name.capitalize()} {entity}"
                        )

                raise forms.ValidationError(
                    mark_safe("<br/>".join(error_messages)),
                    code=f"incomplete_{self.entity_name}",
                )

        return cleaned_data
