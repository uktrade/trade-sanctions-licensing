# Generated by Django 4.2.18 on 2025-02-03 19:27

from django.db import migrations, models


def populate_where_is_the_address(apps, schema_editor):
    """Set the newly-added where_is_the_address field based on the country field."""
    Individual = apps.get_model("apply_for_a_licence", "Individual")
    Organisation = apps.get_model("apply_for_a_licence", "Organisation")
    for individual in Individual.objects.all():
        country = individual.country
        if country == "GB":
            individual.where_is_the_address = "in-uk"
        else:
            individual.where_is_the_address = "outside-uk"

        individual.save(update_fields=["where_is_the_address"])
    for organisation in Organisation.objects.all():
        country = organisation.country
        if country == "GB":
            organisation.where_is_the_address = "in-uk"
        else:
            organisation.where_is_the_address = "outside-uk"

        organisation.save(update_fields=["where_is_the_address"])


def reverse_func(apps, schema_editor):
    Individual = apps.get_model("apply_for_a_licence", "Individual")
    Organisation = apps.get_model("apply_for_a_licence", "Organisation")
    for individual in Individual.objects.all():
        individual.where_is_the_address = None
        individual.save(update_fields=["where_is_the_address"])
    for organisation in Organisation.objects.all():
        organisation.where_is_the_address = None
        organisation.save(update_fields=["where_is_the_address"])


class Migration(migrations.Migration):
    dependencies = [
        ("apply_for_a_licence", "0019_alter_historicalorganisation_business_registered_on_companies_house_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalindividual",
            name="where_is_the_address",
            field=models.CharField(
                blank=True, choices=[("outside-uk", "Outside the UK"), ("in-uk", "In the UK")], max_length=20, null=True
            ),
        ),
        migrations.AddField(
            model_name="historicalorganisation",
            name="where_is_the_address",
            field=models.CharField(
                blank=True, choices=[("outside-uk", "Outside the UK"), ("in-uk", "In the UK")], max_length=20, null=True
            ),
        ),
        migrations.AddField(
            model_name="individual",
            name="where_is_the_address",
            field=models.CharField(
                blank=True, choices=[("outside-uk", "Outside the UK"), ("in-uk", "In the UK")], max_length=20, null=True
            ),
        ),
        migrations.AddField(
            model_name="organisation",
            name="where_is_the_address",
            field=models.CharField(
                blank=True, choices=[("outside-uk", "Outside the UK"), ("in-uk", "In the UK")], max_length=20, null=True
            ),
        ),
        migrations.RunPython(populate_where_is_the_address, reverse_code=reverse_func),
    ]
