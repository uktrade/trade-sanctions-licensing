# Generated by Django 4.2.18 on 2025-01-23 17:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("apply_for_a_licence", "0014_remove_historicalorganisation_id_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="historicalorganisation",
            old_name="uuid_id",
            new_name="id",
        ),
        migrations.RenameField(
            model_name="organisation",
            old_name="uuid_id",
            new_name="id",
        ),
    ]
