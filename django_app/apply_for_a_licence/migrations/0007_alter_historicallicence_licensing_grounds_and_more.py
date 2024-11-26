# Generated by Django 4.2.16 on 2024-11-26 14:29

import django.contrib.postgres.fields
from django.db import migrations, models


def update_old_values(apps, schema_editor):
    # changing 'None of these' -> 'none' and 'Unknown grounds' -> 'unknown'
    Licence = apps.get_model("apply_for_a_licence", "Licence")
    for licence in Licence.objects.all():
        licensing_grounds = licence.licensing_grounds
        if licensing_grounds:
            if "None of these" in licensing_grounds:
                licensing_grounds.remove("None of these")
                licensing_grounds.append("none")
            if "Unknown grounds" in licensing_grounds:
                licensing_grounds.remove("Unknown grounds")
                licensing_grounds.append("unknown")

        licensing_grounds_legal_advisory = licence.licensing_grounds_legal_advisory
        if licensing_grounds_legal_advisory:
            if "None of these" in licensing_grounds_legal_advisory:
                licensing_grounds_legal_advisory.remove("None of these")
                licensing_grounds_legal_advisory.append("none")
            if "Unknown grounds" in licensing_grounds_legal_advisory:
                licensing_grounds_legal_advisory.remove("Unknown grounds")
                licensing_grounds_legal_advisory.append("unknown")

        licence.save()


class Migration(migrations.Migration):

    dependencies = [
        ("apply_for_a_licence", "0006_remove_historicallicence_professional_or_business_service_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicallicence",
            name="licensing_grounds",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        (
                            "civil_society",
                            "Civil society activities that directly promote democracy, human rights or the rule of law in Russia",
                        ),
                        ("energy", "Services necessary for ensuring critical energy supply to any country"),
                        (
                            "divest",
                            "Services necessary for non-Russian persons to divest from Russia, or to wind down business operations in Russia",
                        ),
                        ("humanitarian", "The delivery of humanitarian assistance activity"),
                        (
                            "parent_or_subsidiary_company",
                            "Services to a person connected with Russia by a UK parent company or UK subsidiary of that parent company",
                        ),
                        (
                            "medical_and_pharmaceutical",
                            "Medical and pharmaceutical purposes for the benefit of the civilian population",
                        ),
                        (
                            "safety",
                            "Services required to enable activities necessary for the urgent prevention or mitigation of an event likely to have a serious and significant impact on human health or safety, including the safety of existing infrastructure, or the environment",
                        ),
                        (
                            "food",
                            "Services in connection with the production or distribution of food for the benefit of the civilian population",
                        ),
                        ("unknown", "I do not know"),
                        ("none", "None of these"),
                    ]
                ),
                null=True,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="historicallicence",
            name="licensing_grounds_legal_advisory",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        (
                            "civil_society",
                            "Civil society activities that directly promote democracy, human rights or the rule of law in Russia",
                        ),
                        ("energy", "Services necessary for ensuring critical energy supply to any country"),
                        (
                            "divest",
                            "Services necessary for non-Russian persons to divest from Russia, or to wind down business operations in Russia",
                        ),
                        ("humanitarian", "The delivery of humanitarian assistance activity"),
                        (
                            "parent_or_subsidiary_company",
                            "Services to a person connected with Russia by a UK parent company or UK subsidiary of that parent company",
                        ),
                        (
                            "medical_and_pharmaceutical",
                            "Medical and pharmaceutical purposes for the benefit of the civilian population",
                        ),
                        (
                            "safety",
                            "Services required to enable activities necessary for the urgent prevention or mitigation of an event likely to have a serious and significant impact on human health or safety, including the safety of existing infrastructure, or the environment",
                        ),
                        (
                            "food",
                            "Services in connection with the production or distribution of food for the benefit of the civilian population",
                        ),
                        ("unknown", "I do not know"),
                        ("none", "None of these"),
                    ]
                ),
                null=True,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="licence",
            name="licensing_grounds",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        (
                            "civil_society",
                            "Civil society activities that directly promote democracy, human rights or the rule of law in Russia",
                        ),
                        ("energy", "Services necessary for ensuring critical energy supply to any country"),
                        (
                            "divest",
                            "Services necessary for non-Russian persons to divest from Russia, or to wind down business operations in Russia",
                        ),
                        ("humanitarian", "The delivery of humanitarian assistance activity"),
                        (
                            "parent_or_subsidiary_company",
                            "Services to a person connected with Russia by a UK parent company or UK subsidiary of that parent company",
                        ),
                        (
                            "medical_and_pharmaceutical",
                            "Medical and pharmaceutical purposes for the benefit of the civilian population",
                        ),
                        (
                            "safety",
                            "Services required to enable activities necessary for the urgent prevention or mitigation of an event likely to have a serious and significant impact on human health or safety, including the safety of existing infrastructure, or the environment",
                        ),
                        (
                            "food",
                            "Services in connection with the production or distribution of food for the benefit of the civilian population",
                        ),
                        ("unknown", "I do not know"),
                        ("none", "None of these"),
                    ]
                ),
                null=True,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="licence",
            name="licensing_grounds_legal_advisory",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        (
                            "civil_society",
                            "Civil society activities that directly promote democracy, human rights or the rule of law in Russia",
                        ),
                        ("energy", "Services necessary for ensuring critical energy supply to any country"),
                        (
                            "divest",
                            "Services necessary for non-Russian persons to divest from Russia, or to wind down business operations in Russia",
                        ),
                        ("humanitarian", "The delivery of humanitarian assistance activity"),
                        (
                            "parent_or_subsidiary_company",
                            "Services to a person connected with Russia by a UK parent company or UK subsidiary of that parent company",
                        ),
                        (
                            "medical_and_pharmaceutical",
                            "Medical and pharmaceutical purposes for the benefit of the civilian population",
                        ),
                        (
                            "safety",
                            "Services required to enable activities necessary for the urgent prevention or mitigation of an event likely to have a serious and significant impact on human health or safety, including the safety of existing infrastructure, or the environment",
                        ),
                        (
                            "food",
                            "Services in connection with the production or distribution of food for the benefit of the civilian population",
                        ),
                        ("unknown", "I do not know"),
                        ("none", "None of these"),
                    ]
                ),
                null=True,
                size=None,
            ),
        ),
        migrations.RunPython(update_old_values),
    ]
