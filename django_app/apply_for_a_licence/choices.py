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


class NationalityAndLocation(models.TextChoices):
    uk_national_uk_location = "uk_national_uk_location", "UK national located in the UK"
    uk_national_non_uk_location = "uk_national_non_uk_location", "UK national located outside the UK"
    dual_national_uk_location = "dual_national_uk_location", "Dual national (includes UK) located in the UK"
    dual_national_non_uk_location = "dual_national_non_uk_location", "Dual national (includes UK) located outside the UK"
    non_uk_national_uk_location = "non_uk_national_uk_location", "Non-UK national located in the UK"
