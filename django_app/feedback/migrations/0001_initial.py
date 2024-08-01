# Generated by Django 4.2.14 on 2024-07-31 08:00

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FeedbackItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
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
                (
                    "did_you_experience_any_issues",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("no", "I did not experience any issues"),
                                ("not_found", "I did not find what I was looking for"),
                                ("difficult", "I found it difficult to navigate"),
                                ("lacks_features", "The system lacks the feature I need"),
                                ("other", "Other"),
                            ],
                            max_length=32,
                        ),
                        blank=True,
                        null=True,
                        size=None,
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
                ("id", models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name="ID")),
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
                (
                    "did_you_experience_any_issues",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("no", "I did not experience any issues"),
                                ("not_found", "I did not find what I was looking for"),
                                ("difficult", "I found it difficult to navigate"),
                                ("lacks_features", "The system lacks the feature I need"),
                                ("other", "Other"),
                            ],
                            max_length=32,
                        ),
                        blank=True,
                        null=True,
                        size=None,
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
