# Generated by Django 3.2.2 on 2022-10-25 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation_in_area', '0004_alter_evaluationaspect_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monthevaluation',
            name='evaluator',
            field=models.CharField(max_length=100),
        ),
    ]
