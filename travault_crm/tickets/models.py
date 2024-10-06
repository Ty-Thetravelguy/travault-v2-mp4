from crm.models import Company, Contact 
from agencies.models import Agency
from django.db import models
from django.conf import settings 

class TicketSubject(models.Model):
    subject = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.subject

class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    CATEGORY_TYPE_CHOICES = [
        ('client', 'Client'),
        ('agency', 'Agency'),
    ]
    
    CATEGORY_CHOICES_CLIENT = [
        ('complaint', 'Complaint'),
        ('query', 'Query'),
        ('request', 'Request'),
    ]
    
    CATEGORY_CHOICES_AGENCY = [
        ('consultant_error', 'Consultant Error'),
        ('supplier_error', 'Supplier Error'),
        ('supplier_query', 'Supplier Query'),
        ('system_error', 'System Error'),
        ('system_query', 'System Query'),
        ('system_enhancement', 'System Enhancement'),
    ]

    
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.SET_NULL) 
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE) 
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES)
    category = models.CharField(max_length=50)
    subject = models.ForeignKey(TicketSubject, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=20, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
