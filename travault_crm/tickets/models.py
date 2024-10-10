from crm.models import Company, Contact 
from agencies.models import Agency, CustomUser
from django.db import models
from django.conf import settings 
from django.utils import timezone


class TicketSubject(models.Model):
    subject = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.subject

class Ticket(models.Model):

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

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

    def get_category_display(self):
        if self.category_type == 'client':
            choices = dict(self.CATEGORY_CHOICES_CLIENT)
        elif self.category_type == 'agency':
            choices = dict(self.CATEGORY_CHOICES_AGENCY)
        else:
            return self.category
        return choices.get(self.category, self.category)
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.SET_NULL) 
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE) 
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    received_from = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_tickets'
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES_CLIENT)
    subject = models.ForeignKey(TicketSubject, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TicketAction(models.Model):
    ACTION_TYPES = [
        ('action_taken', 'Action Taken'),
        ('update', 'Update'),
        ('response', 'Response'),
        ('outcome', 'Outcome'),
    ]

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    details = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_actions'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='updated_actions'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_action_type_display()} for Ticket #{self.ticket.id}"