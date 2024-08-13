from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def readable_location(nationality_and_location: str) -> str:
    """Returns a human-readable value for whether the location is in the UK."""
    if nationality_and_location in ["uk_national_uk_location", "dual_national_uk_location", "non_uk_national_uk_location"]:
        readable_location = "The UK"
    else:
        readable_location = "Outside the UK"
    return readable_location
