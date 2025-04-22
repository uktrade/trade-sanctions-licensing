from apply_for_a_licence.choices import YES_NO_CHOICES
from django import forms


class YesNoBooleanField(forms.TypedChoiceField):
    def __init__(self, *args: object, **kwargs: object) -> None:
        kwargs["coerce"] = lambda x: x.lower() == "true"
        kwargs.setdefault("choices", YES_NO_CHOICES)
        super().__init__(*args, **kwargs)
