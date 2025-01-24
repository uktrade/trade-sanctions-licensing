# Generated by Django 4.2.18 on 2025-01-23 17:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("apply_for_a_licence", "0013_historicalorganisation_uuid_id_organisation_uuid_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalorganisation",
            name="id",
        ),
        migrations.RemoveField(
            model_name="organisation",
            name="id",
        ),
        migrations.AlterField(
            model_name="historicalorganisation",
            name="uuid_id",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
        ),
        migrations.AlterField(
            model_name="organisation",
            name="uuid_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
