from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def location(nationality_and_location: str) -> bool:
    print(nationality_and_location)
    if nationality_and_location in ["uk_national_uk_location", "dual_national_uk_location", "non_uk_national_uk_location"]:
        location = "The UK"
    else:
        location = "Outside the UK"
    return location


@register.filter
@stringfilter
def nationality(nationality_and_location: str) -> str:
    if nationality_and_location in ["uk_national_uk_location", "uk_national_non_uk_location"]:
        nationality = "UK national"
    elif nationality_and_location in ["dual_national_uk_location", "dual_national_non_uk_location"]:
        nationality = "Dual national (includes UK)"
    else:
        nationality = "Non-UK national"
    return nationality
