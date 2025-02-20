# Generated by Django 4.2.19 on 2025-02-19 11:44

from django.db import migrations, models


def populate_is_applicant(apps, schema_editor):
    Licence = apps.get_model("apply_for_a_licence", "Licence")
    for licence in Licence.objects.filter(who_do_you_want_the_licence_to_cover="myself"):
        # we can assume that the first Individual created was the applicant (your-details)
        applicant_individual = licence.individuals.first()

        # we can confirm this by checking the name
        if applicant_individual.full_name == licence.applicant_full_name:
            applicant_individual.is_applicant = True
            applicant_individual.save(update_fields=["is_applicant"])


def remove_is_applicant(apps, schema_editor):
    Individual = apps.get_model("apply_for_a_licence", "Individual")
    for individual in Individual.objects.all():
        individual.is_applicant = False
        individual.save(update_fields=["is_applicant"])


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
