from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def location(nationality_and_location: str) -> bool:
    if nationality_and_location in ["uk_national_uk_location", "dual_national_uk_location", "non_uk_national_uk_location"]:
        location = "The UK"
    else:
        location = "Outside the UK"
    return location
