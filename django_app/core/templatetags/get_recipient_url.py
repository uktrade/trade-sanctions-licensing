from django import template
from django.http import HttpResponse
from django.urls import reverse

register = template.Library()


@register.simple_tag
def get_recipient_url(location: str, recipient_uuid: str) -> HttpResponse:
    return reverse("add_a_recipient", kwargs={"location": location, "recipient_uuid": recipient_uuid})
