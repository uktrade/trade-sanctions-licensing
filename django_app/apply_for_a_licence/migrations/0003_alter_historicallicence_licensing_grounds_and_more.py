# Generated by Django 4.2.15 on 2024-09-19 16:39

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apply_for_a_licence", "0002_alter_historicallicence_who_do_you_want_the_licence_to_cover_and_more"),
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
                    ]
                ),
                null=True,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="historicallicence",
            name="type_of_service",
            field=models.CharField(
                choices=[
                    ("professional_and_business", "Professional and business services (Russia)"),
                    ("energy_related", "Energy-related services (Russia)"),
                    (
                        "infrastructure_and_tourism_related",
                        "Infrastructure and tourism-related services to non-government controlled Ukrainian territories (Russia)",
                    ),
                    (
                        "interception_or_monitoring",
                        "Interception or monitoring services (Russia, Belarus, Iran, Myanmar, Syria and Venezuela)",
                    ),
                    (
                        "mining_manufacturing_or_computer",
                        "Mining, manufacturing or computer services (Democratic People’s Republic of Korea)",
                    ),
                    ("ships_or_aircraft_related", "Ships or aircraft-related services (Democratic People's Republic of Korea)"),
                ]
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
                    ]
                ),
                null=True,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="licence",
            name="type_of_service",
            field=models.CharField(
                choices=[
                    ("professional_and_business", "Professional and business services (Russia)"),
                    ("energy_related", "Energy-related services (Russia)"),
                    (
                        "infrastructure_and_tourism_related",
                        "Infrastructure and tourism-related services to non-government controlled Ukrainian territories (Russia)",
                    ),
                    (
                        "interception_or_monitoring",
                        "Interception or monitoring services (Russia, Belarus, Iran, Myanmar, Syria and Venezuela)",
                    ),
                    (
                        "mining_manufacturing_or_computer",
                        "Mining, manufacturing or computer services (Democratic People’s Republic of Korea)",
                    ),
                    ("ships_or_aircraft_related", "Ships or aircraft-related services (Democratic People's Republic of Korea)"),
                ]
            ),
        ),
    ]
