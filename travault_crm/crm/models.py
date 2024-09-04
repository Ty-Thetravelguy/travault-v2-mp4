# crm/models.py

from django.db import models
from agencies.models import Agency

class Company(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='companies')
    company_name = models.CharField(max_length=255)
    company_owner = models.CharField(max_length=255)  # Or a ForeignKey to User if needed
    create_date = models.DateTimeField(auto_now_add=True)
    last_activity_date = models.DateTimeField(auto_now=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    company_type = models.CharField(max_length=50, blank=True, null=True)  # E.g., client, partner, etc.

    def __str__(self):
        return self.company_name
