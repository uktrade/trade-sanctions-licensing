from core.models import BaseModel
from django.contrib.postgres.fields import ArrayField
from django.db import models

from .choices import DidYouExperienceAnyIssues, RatingChoices


class FeedbackItem(BaseModel):
    rating = models.IntegerField(choices=RatingChoices.choices, blank=False)
    did_you_experience_any_issues = ArrayField(
        base_field=models.CharField(max_length=32, choices=DidYouExperienceAnyIssues.choices), blank=True, null=True
    )
    how_we_could_improve_the_service = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)

    def get_did_you_experience_any_issues_display(self) -> str:
        display_list = []
        if self.did_you_experience_any_issues:
            display_list += [dict(DidYouExperienceAnyIssues.choices)[value] for value in self.did_you_experience_any_issues]
        display = ",\n".join(display_list)
        return display
