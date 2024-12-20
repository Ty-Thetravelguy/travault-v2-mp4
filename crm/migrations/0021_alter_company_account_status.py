# Generated by Django 4.2.16 on 2024-12-08 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0020_alter_company_industry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='account_status',
            field=models.CharField(choices=[('Lead', 'Lead'), ('Qualified', 'Qualified'), ('In Discussion', 'In Discussion'), ('Account Form Sent', 'Account Form Sent'), ('New Client', 'New Client'), ('Trading', 'Trading'), ('No longer Trading', 'No longer Trading'), ('On hold', 'On hold'), ('Closed - Won', 'Closed - Won'), ('Closed - Lost', 'Closed - Lost'), ('Other', 'Other')], default='Lead', max_length=255),
        ),
    ]
