# Generated by Django 4.2.16 on 2024-12-04 17:51
from django.db import migrations

def create_default_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    # Check if site exists first
    if not Site.objects.filter(domain='travault-686ad8887c30.herokuapp.com').exists():
        Site.objects.create(
            domain='travault-686ad8887c30.herokuapp.com',
            name='Travault CRM'
        )

class Migration(migrations.Migration):
    dependencies = [
        ('agencies', '0010_remove_agency_name'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(create_default_site),
    ]