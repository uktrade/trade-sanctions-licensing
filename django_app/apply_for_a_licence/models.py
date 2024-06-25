from core.models import BaseModel
from django.contrib.sessions.models import Session
from django.db import models

from . import choices


class Licence(BaseModel):
    who_do_you_want_the_licence_to_cover = models.CharField(
        max_length=255,
        choices=choices.WhoDoYouWantTheLicenceToCoverChoices.choices,
        blank=True,
        null=True,
    )
    user_email_address = models.EmailField(
        blank=True,
        null=True,
    )
    user_email_verification = models.ForeignKey("UserEmailVerification", on_delete=models.CASCADE, blank=True, null=True)
    your_details_full_name = models.CharField(max_length=255)
    your_details_name_of_business_you_work_for = models.CharField(max_length=300, verbose_name="Business you work for")
    your_details_role = models.CharField(max_length=255)
    held_previous_licence = models.CharField(
        choices=choices.YesNoChoices.choices,
        max_length=11,
        blank=False,
    )
    previous_licences = models.TextField(null=True, blank=True)


class UserEmailVerification(BaseModel):
    user_session = models.ForeignKey(Session, on_delete=models.CASCADE)
    email_verification_code = models.CharField(max_length=6)
    date_created = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
