from crm.models import Company, Contact 
from agencies.models import Agency
from django.db import models
from django.conf import settings 


class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.SET_NULL) 
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE) 
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, default='open')
    ticket_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
