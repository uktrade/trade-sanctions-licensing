# Generated by Django 4.2.17 on 2025-01-15 13:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("apply_for_a_licence", "0008_historicallicence_user_licence_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicallicence",
            name="status",
            field=models.CharField(choices=[("draft", "Draft"), ("submitted", "Submitted")], default="draft", max_length=10),
        ),
        migrations.AddField(
            model_name="historicallicence",
            name="submitted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="licence",
            name="status",
            field=models.CharField(choices=[("draft", "Draft"), ("submitted", "Submitted")], default="draft", max_length=10),
        ),
        migrations.AddField(
            model_name="licence",
            name="submitted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="licence",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="licence_applications",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
