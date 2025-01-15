import uuid

from django.db import models
from simple_history.models import HistoricalRecords


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True

    @property
    def _history_user(self):
        # todo - remove when OneLogin is enabled
        return None


class BaseModelID(BaseModel):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True
