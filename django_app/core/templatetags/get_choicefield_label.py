from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def location(form, field_name: str) -> bool:
    return dict(form.fields[field_name].choices)[form.cleaned_data[field_name]]
