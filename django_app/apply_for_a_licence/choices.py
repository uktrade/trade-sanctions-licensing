from crispy_forms_gds.choices import Choice
from django.db import models

YES_NO_CHOICES = (
    Choice(True, "Yes"),
    Choice(False, "No"),
)


class WhoDoYouWantTheLicenceToCoverChoices(models.TextChoices):
    business = "business", "A business or several businesses"
    individual = "individual", "A named individual or several named individuals"
    myself = "myself", "Myself"


class YesNoChoices(models.TextChoices):
    yes = "yes", "Yes"
    no = "no", "No"
