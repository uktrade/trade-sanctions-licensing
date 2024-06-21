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
    your_details_full_name = models.CharField(max_length=255)
    your_details_name_of_business_you_work_for = models.CharField(max_length=300, verbose_name="Business you work for")
    your_details_role = models.CharField(max_length=255)
