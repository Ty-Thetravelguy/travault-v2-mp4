# crm/models.py

from django.db import models
from agencies.models import Agency
from django.conf import settings

INDUSTRY_CHOICES = [
    ('Technology', 'Technology'),
    ('Healthcare', 'Healthcare'),
    ('Finance', 'Finance'),
    ('Retail', 'Retail'),
    ('Manufacturing', 'Manufacturing'),
    ('Energy', 'Energy'),
    ('Transportation and Logistics', 'Transportation and Logistics'),
    ('Construction', 'Construction'),
    ('Education', 'Education'),
    ('Hospitality and Tourism', 'Hospitality and Tourism'),
    ('Real Estate', 'Real Estate'),
    ('Media and Entertainment', 'Media and Entertainment'),
    ('Agriculture', 'Agriculture'),
    ('Pharmaceuticals', 'Pharmaceuticals'),
    ('Telecommunications', 'Telecommunications'),
    ('Legal and Professional Services', 'Legal and Professional Services'),
    ('Fashion and Apparel', 'Fashion and Apparel'),
    ('Automotive', 'Automotive'),
    ('Mining and Metals', 'Mining and Metals'),
    ('Aerospace and Defence', 'Aerospace and Defence'),
    ('Environmental Services', 'Environmental Services'),
]

COMPANY_TYPE_CHOICES = [
    ('Prospect Client', 'Prospect Client'),
    ('White Glove Client', 'White Glove Client'),
    ('Online Client', 'Online Client'),
    ('Mix of On and Offline', 'Mix of On and Offline'),
    ('Former Client', 'Former Client'),
    ('Supplier', 'Supplier'),
    ('Other', 'Other'),
]

CLIENT_TYPE_CHOICES = [
    ('Travel', 'Travel'),
    ('Meetings and Events', 'Meetings and Events'),
]

ACCOUNT_STATUS_CHOICES = [
    ('Lead', 'Lead'),
    ('New Client', 'New Client'),
    ('Trading', 'Trading'),
    ('No longer Trading', 'No longer Trading'),
    ('On hold', 'On hold'),
    ('Other', 'Other'),
]

class Company(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='companies', null=False)   
    company_name = models.CharField(max_length=255, blank=False, null=False)
    street_address = models.CharField(max_length=255, blank=False, null=False)
    city = models.CharField(max_length=100, blank=False, null=False)
    state_province = models.CharField(max_length=100, blank=False, null=False)
    postal_code = models.CharField(max_length=20, blank=False, null=False)
    country = models.CharField(max_length=100, blank=False, null=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    linkedin_social_page = models.URLField(blank=True, null=True)
    industry = models.CharField(max_length=255, choices=INDUSTRY_CHOICES, blank=False, null=False)
    company_type = models.CharField(max_length=255, choices=COMPANY_TYPE_CHOICES, default='Prospect Client')
    company_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    ops_team = models.CharField(max_length=255, blank=True, null=True)
    client_type = models.CharField(max_length=255, choices=CLIENT_TYPE_CHOICES, default='Travel')
    account_status = models.CharField(max_length=255, choices=ACCOUNT_STATUS_CHOICES, default='Lead')
    create_date = models.DateTimeField(auto_now_add=True) 
    linked_companies = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='linked_to')

    # New fields (these will be added in a new migration)


    def __str__(self):
        return self.company_name


class Contact(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True, null=True)  # New field
    job_title = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)
    is_primary_contact = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.company})"