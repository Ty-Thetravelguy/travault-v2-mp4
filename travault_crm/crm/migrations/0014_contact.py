# Generated by Django 5.1 on 2024-09-10 06:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0013_remove_company_company_address_alter_company_city_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('job_title', models.CharField(max_length=100)),
                ('department', models.CharField(blank=True, max_length=100, null=True)),
                ('is_primary_contact', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True, null=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='crm.company')),
            ],
        ),
    ]