# Generated by Django 5.1 on 2024-09-01 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agencies', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]