# Generated by Django 5.1 on 2024-09-05 05:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='agency',
        ),
        migrations.RemoveField(
            model_name='company',
            name='country',
        ),
        migrations.RemoveField(
            model_name='company',
            name='create_date',
        ),
        migrations.RemoveField(
            model_name='company',
            name='last_activity_date',
        ),
        migrations.RemoveField(
            model_name='company',
            name='phone_number',
        ),
        migrations.AddField(
            model_name='company',
            name='account_status',
            field=models.CharField(choices=[('Lead', 'Lead'), ('New Client', 'New Client'), ('Trading', 'Trading'), ('No longer Trading', 'No longer Trading'), ('On hold', 'On hold')], default='Lead', max_length=255),
        ),
        migrations.AddField(
            model_name='company',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='client_type',
            field=models.CharField(choices=[('Travel', 'Travel'), ('Meetings and Events', 'Meetings and Events')], default='Travel', max_length=255),
        ),
        migrations.AddField(
            model_name='company',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='linkedin_social_page',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='ops_team',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='company',
            name='company_type',
            field=models.CharField(choices=[('Prospect Client', 'Prospect Client'), ('White Glove Client', 'White Glove Client'), ('Online Client', 'Online Client'), ('Mix of On and Offline', 'Mix of On and Offline'), ('Former Client', 'Former Client'), ('Supplier', 'Supplier'), ('Other', 'Other')], default='Prospect Client', max_length=255),
        ),
        migrations.AlterField(
            model_name='company',
            name='industry',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
