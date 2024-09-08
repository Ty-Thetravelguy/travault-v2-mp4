from django.db import migrations

def update_company_addresses(apps, schema_editor):
    Company = apps.get_model('crm', 'Company')
    for company in Company.objects.all():
        # Split the existing company_address field
        address_parts = company.company_address.split(', ')
        
        # Update the company_address field with a structured format
        company.company_address = f"{address_parts[0] if len(address_parts) > 0 else 'Unknown'}, " \
                                  f"{address_parts[1] if len(address_parts) > 1 else 'Unknown'}, " \
                                  f"{address_parts[2] if len(address_parts) > 2 else 'Unknown'}, " \
                                  f"{address_parts[3] if len(address_parts) > 3 else 'Unknown'}, " \
                                  f"{address_parts[4] if len(address_parts) > 4 else 'Unknown'}"
        
        company.save()

class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0009_company_linked_companies'),
    ]

    operations = [
        migrations.RunPython(update_company_addresses),
    ]