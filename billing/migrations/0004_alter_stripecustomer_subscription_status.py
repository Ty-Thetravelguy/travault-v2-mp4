# Generated by Django 5.1 on 2024-11-21 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_alter_stripecustomer_stripe_customer_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripecustomer',
            name='subscription_status',
            field=models.CharField(default='inactive', max_length=50),
        ),
    ]
