# Generated by Django 4.2.18 on 2025-01-27 12:55

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("apply_for_a_licence", "0017_alter_organisation_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalindividual",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AddField(
            model_name="individual",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
