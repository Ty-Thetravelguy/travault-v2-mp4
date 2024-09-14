#activity_log/models.py

from django.db import models
from django.conf import settings
from crm.models import Company, Contact

class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('ticket', 'Ticket'),
        ('deal', 'Deal'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='activity_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    related_contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.subject}"