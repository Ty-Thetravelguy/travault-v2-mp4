# Generated by Django 5.1 on 2024-11-17 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agencies', '0006_agency_name_alter_agency_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agency',
            name='name',
        ),
    ]
