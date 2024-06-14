# Generated by Django 4.2.13 on 2024-05-20 09:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FeedbackItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "rating",
                    models.IntegerField(
                        choices=[
                            (1, "Very dissatisfied"),
                            (2, "Dissatisfied"),
                            (3, "Neutral"),
                            (4, "Satisfied"),
                            (5, "Very satisfied"),
                        ]
                    ),
                ),
                ("how_we_could_improve_the_service", models.TextField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="HistoricalFeedbackItem",
            fields=[
                ("id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("modified_at", models.DateTimeField(blank=True, editable=False)),
                (
                    "rating",
                    models.IntegerField(
                        choices=[
                            (1, "Very dissatisfied"),
                            (2, "Dissatisfied"),
                            (3, "Neutral"),
                            (4, "Satisfied"),
                            (5, "Very satisfied"),
                        ]
                    ),
                ),
                ("how_we_could_improve_the_service", models.TextField(blank=True, null=True)),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                ("history_type", models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1)),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "verbose_name": "historical feedback item",
                "verbose_name_plural": "historical feedback items",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
