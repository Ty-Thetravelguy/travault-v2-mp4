# Generated by Django 5.1 on 2024-11-20 18:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agencies', '0009_alter_agency_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agency',
            name='name',
        ),
    ]
