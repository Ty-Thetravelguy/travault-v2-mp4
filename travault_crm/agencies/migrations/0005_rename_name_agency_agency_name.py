# Generated by Django 5.1 on 2024-09-04 06:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agencies', '0004_alter_agency_business_focus_alter_agency_employees'),
    ]

    operations = [
        migrations.RenameField(
            model_name='agency',
            old_name='name',
            new_name='agency_name',
        ),
    ]