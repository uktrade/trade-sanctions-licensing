import uuid

from django.db import models
from simple_history.models import HistoricalRecords


class BaseModel(models.Model):
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    modified_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    history: HistoricalRecords = HistoricalRecords(inherit=True)

    class Meta:
        abstract: bool = True


class BaseModelID(BaseModel):
    id: models.UUIDField = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract: bool = True
