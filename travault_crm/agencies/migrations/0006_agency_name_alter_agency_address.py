# Generated by Django 5.1 on 2024-09-17 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agencies', '0005_rename_name_agency_agency_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='agency',
            name='name',
            field=models.CharField(default='Default Agency Name', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='agency',
            name='address',
            field=models.CharField(max_length=255),
        ),
    ]
