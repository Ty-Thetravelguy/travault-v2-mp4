# Generated by Django 5.1 on 2024-10-04 05:28

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity_log', '0007_call_users'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='email_users', to=settings.AUTH_USER_MODEL),
        ),
    ]
