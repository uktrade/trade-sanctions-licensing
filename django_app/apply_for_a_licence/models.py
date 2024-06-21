from core.models import BaseModel
from django.db import models

from . import choices


class Licence(BaseModel):
    who_do_you_want_the_licence_to_cover = models.CharField(
        max_length=255,
        choices=choices.WhoDoYouWantTheLicenceToCoverChoices.choices,
        blank=True,
        null=True,
    )
    held_previous_licence = models.CharField(
        choices=choices.YesNoChoices.choices,
        max_length=11,
        blank=False,
    )
    previous_licences = models.TextField(null=True, blank=True)
