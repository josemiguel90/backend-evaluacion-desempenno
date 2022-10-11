# Generated by Django 3.2.2 on 2022-10-11 21:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation_in_area', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='area',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='evaluation_in_area.evaluationarea'),
        ),
    ]
