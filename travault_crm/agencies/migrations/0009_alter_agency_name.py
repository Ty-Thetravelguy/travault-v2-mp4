# Generated by Django 5.1 on 2024-11-17 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agencies', '0008_agency_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agency',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
