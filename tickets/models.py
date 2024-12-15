from crm.models import Company, Contact 
from agencies.models import Agency, CustomUser
from django.db import models
from django.conf import settings 
from django.utils import timezone
from django.core.exceptions import ValidationError


class TicketSubject(models.Model):
    """
    Model to store unique ticket subjects per agency.
    
    Each subject is associated with a specific agency and must be unique within
    that agency's context, though the same subject can exist for different agencies.
    """
    subject = models.CharField(max_length=100)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['subject', 'agency']  # Subjects can be duplicated across agencies but unique within an agency

    def __str__(self):
        return self.subject


class Ticket(models.Model):
    """
    Core model for tracking support tickets in the system.
    
    Handles all ticket-related data including status, priority, categorization,
    and relationships to companies, contacts, and users.
    """

    # Status options for tickets
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('dev', 'Development'),
        ('closed', 'Closed'),
    ]

    # Priority levels for tickets
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    # Main category types
    CATEGORY_TYPE_CHOICES = [
        ('client', 'Client'),
        ('agency', 'Agency'),
    ]
    
    # Subcategories for client tickets
    CATEGORY_CHOICES_CLIENT = [
        ('complaint', 'Complaint'),
        ('query', 'Query'),
        ('request', 'Request'),
    ]
    
    # Subcategories for agency tickets
    CATEGORY_CHOICES_AGENCY = [
        ('consultant_error', 'Consultant Error'),
        ('supplier_error', 'Supplier Error'),
        ('supplier_query', 'Supplier Query'),
        ('system_error', 'System Error'),
        ('system_query', 'System Query'),
        ('system_enhancement', 'System Enhancement'),
    ]

    # Core relationships
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.SET_NULL) 
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE) 
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_to'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='updated_tickets'
    )

    # Ticket details
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    category_type = models.CharField(max_length=30, choices=CATEGORY_TYPE_CHOICES)
    category = models.CharField(max_length=50) 
    subject = models.ForeignKey(TicketSubject, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_category_display(self):
        """Returns the human-readable category based on category type."""
        if self.category_type == 'client':
            choices = dict(self.CATEGORY_CHOICES_CLIENT)
        elif self.category_type == 'agency':
            choices = dict(self.CATEGORY_CHOICES_AGENCY)
        else:
            return self.category
        return choices.get(self.category, self.category)

    def save(self, *args, **kwargs):
        """
        Custom save method with validation for ticket status changes.
        
        Prevents non-admin users from reopening closed tickets.
        """
        if self.pk:  # If the ticket already exists
            original = Ticket.objects.get(pk=self.pk)
            if (
                original.status == 'closed' 
                and self.status != 'closed' 
                and not getattr(self, '_is_admin_override', False)
            ):
                raise ValidationError('Closed tickets cannot be reopened by non-admin users.')
        super(Ticket, self).save(*args, **kwargs)

    def admin_override_save(self, *args, **kwargs):
        """Special save method for admin users to override normal status restrictions."""
        self._is_admin_override = True
        self.save(*args, **kwargs)


class TicketAction(models.Model):
    """
    Model to track actions and updates made to tickets.
    
    Records various types of actions, who performed them, and when they occurred.
    """
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
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True, 
        related_name='created_actions'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True, 
        related_name='updated_actions'
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_system_generated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_action_type_display()} for Ticket #{self.ticket.id}"