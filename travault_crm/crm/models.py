# crm/models.py

from django.db import models
from agencies.models import Agency
from django.conf import settings

class Company(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='companies', null=True)   
    company_name = models.CharField(max_length=255)
    company_address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    linkedin_social_page = models.URLField(blank=True, null=True)
    company_type = models.CharField(max_length=255, choices=[
        ('Prospect Client', 'Prospect Client'),
        ('White Glove Client', 'White Glove Client'),
        ('Online Client', 'Online Client'),
        ('Mix of On and Offline', 'Mix of On and Offline'),
        ('Former Client', 'Former Client'),
        ('Supplier', 'Supplier'),
        ('Other', 'Other'),
    ],
    default='Prospect Client'
    )
    company_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    ops_team = models.CharField(max_length=255, blank=True, null=True)
    client_type = models.CharField(
        max_length=255,
        choices=[
            ('Travel', 'Travel'),
            ('Meetings and Events', 'Meetings and Events')
        ],
        default='Travel'  # Set a default value here
    )
    account_status = models.CharField(
        max_length=255,
        choices=[
            ('Lead', 'Lead'),
            ('New Client', 'New Client'),
            ('Trading', 'Trading'),
            ('No longer Trading', 'No longer Trading'),
            ('On hold', 'On hold')
        ],
        default='Lead'  # Provide a default value here
    )

    def __str__(self):
        return self.company_name
