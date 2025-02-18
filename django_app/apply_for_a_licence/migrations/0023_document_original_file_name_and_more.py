# Generated by Django 4.2.19 on 2025-02-13 15:28

import apply_for_a_licence.utils
import core.document_storage
from django.db import migrations, models


def add_original_file_name(apps, schema_editor):
    # todo - check this
    Document = apps.get_model("apply_for_a_licence", "Document")
    for document in Document.objects.all():
        document.original_file_name = document.file.file.original_name
        document.save()


def remove_original_file_name(apps, schema_editor):
    Document = apps.get_model("apply_for_a_licence", "Document")
    for document in Document.objects.all():
        document.original_file_name = None
        document.save()


class Migration(migrations.Migration):

    dependencies = [
        ("apply_for_a_licence", "0022_alter_historicallicence_regimes_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="document",
            name="original_file_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="historicaldocument",
            name="original_file_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="document",
            name="file",
            field=models.FileField(
                blank=True,
                max_length=340,
                null=True,
                storage=core.document_storage.PermanentDocumentStorage(),
                upload_to=apply_for_a_licence.utils.get_file_s3_key,
            ),
        ),
        migrations.RunPython(add_original_file_name, remove_original_file_name),
    ]
