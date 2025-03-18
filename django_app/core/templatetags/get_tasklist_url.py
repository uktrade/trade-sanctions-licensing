from django import template
from django.http import HttpResponse
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def get_tasklist_url(context, pk: str) -> HttpResponse:
    # todo: update to tasklist url as part of DST-946
    return reverse("start", kwargs={"pk": pk})
