# Generated by Django 5.1 on 2024-10-11 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0012_ticketaction_updated_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketaction',
            name='is_system_generated',
            field=models.BooleanField(default=False),
        ),
    ]