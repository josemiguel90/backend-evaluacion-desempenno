# Generated by Django 3.2.2 on 2022-11-08 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation_in_area', '0012_populate_melia_aspect_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthevaluation',
            name='melia_observations',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.DeleteModel(
            name='MeliaMonthEvaluationObservation',
        ),
    ]
