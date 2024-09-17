# activity_log/models.py

from django.db import models
from django.contrib.auth import get_user_model
from crm.models import Company, Contact
from django_ckeditor_5.fields import CKEditor5Field  # Import CKEditor5Field

User = get_user_model()

class Meeting(models.Model):
    OUTCOME_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Rescheduled', 'Rescheduled'),
        ('No-show', 'No-show'),
        ('Cancelled', 'Cancelled'),
    ]

    LOCATION_CHOICES = [
        ('Online', 'Online'),
        ('In-person', 'In-person'),
    ]

    DURATION_CHOICES = [(i, f"{i} minutes") for i in range(15, 481, 15) if i % 15 == 0]

    subject = models.CharField(max_length=255)
    attendees = models.ManyToManyField(Contact, related_name='meetings')
    associated_companies = models.ManyToManyField(Company, related_name='meetings')
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(choices=DURATION_CHOICES)
    details = CKEditor5Field('Details', config_name='default', default='')
    to_do_task_date = models.DateField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings')
    agency = models.ForeignKey('agencies.Agency', on_delete=models.CASCADE, related_name='meetings')  # Ensure agency field is added
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} - {self.date}"

    class Meta:
        ordering = ['-date', '-time']