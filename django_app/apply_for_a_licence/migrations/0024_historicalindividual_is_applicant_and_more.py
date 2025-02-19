# Generated by Django 4.2.19 on 2025-02-19 11:44

from django.db import migrations, models


def populate_is_applicant(apps, schema_editor):
    # todo - check this
    Document = apps.get_model("apply_for_a_licence", "Document")
    for document in Document.objects.all():
        document.original_file_name = document.file.file.original_name
        document.save()


def remove_is_applicant(apps, schema_editor):
    Document = apps.get_model("apply_for_a_licence", "Document")
    for document in Document.objects.all():
        document.original_file_name = None
        document.save()


class Migration(migrations.Migration):

    dependencies = [
        ("apply_for_a_licence", "0023_document_original_file_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalindividual",
            name="is_applicant",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="individual",
            name="is_applicant",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(populate_is_applicant, remove_is_applicant),
    ]
