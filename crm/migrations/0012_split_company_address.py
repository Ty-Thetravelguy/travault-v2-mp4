from django.db import migrations

def split_company_address(apps, schema_editor):
    Company = apps.get_model('crm', 'Company')
    for company in Company.objects.all():
        if company.company_address:
            parts = company.company_address.split(', ')
            company.street_address = parts[0] if len(parts) > 0 else ''
            company.city = parts[1] if len(parts) > 1 else ''
            company.state_province = parts[2] if len(parts) > 2 else ''
            company.postal_code = parts[3] if len(parts) > 3 else ''
            company.country = parts[4] if len(parts) > 4 else ''
            company.save()

class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0011_company_city_company_country_company_postal_code_and_more'),  # replace XXXX with the number of your previous migration
    ]

    operations = [
        migrations.RunPython(split_company_address),
    ]