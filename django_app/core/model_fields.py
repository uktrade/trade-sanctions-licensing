from apply_for_a_licence.choices import YES_NO_CHOICES
from core.form_fields import YesNoBooleanField as YesNoBooleanFieldFormField
from django.db import models


class YesNoBooleanField(models.BooleanField):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = YES_NO_CHOICES
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {"form_class": YesNoBooleanFieldFormField}
        return super().formfield(**{**defaults, **kwargs})
