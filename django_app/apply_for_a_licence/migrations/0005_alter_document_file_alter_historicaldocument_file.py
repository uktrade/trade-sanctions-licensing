# Generated by Django 4.2.15 on 2024-10-04 11:27

import core.document_storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apply_for_a_licence", "0004_alter_historicallicence_type_of_service_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="file",
            field=models.FileField(
                blank=True, max_length=340, null=True, storage=core.document_storage.PermanentDocumentStorage(), upload_to=""
            ),
        ),
        migrations.AlterField(
            model_name="historicaldocument",
            name="file",
            field=models.TextField(blank=True, max_length=340, null=True),
        ),
    ]