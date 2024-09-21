# activity_log/models.py

from django.db import models
from crm.models import Company, Contact
from django.contrib.auth import get_user_model

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
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='meetings')  # Link to one company
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings')
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(choices=DURATION_CHOICES)
    details = models.TextField('Details', default='', blank=True)
    to_do_task_date = models.DateField(null=True, blank=True)
    to_do_task_message = models.TextField('To Do Task Message', null=True, blank=True)  # New Field

    attendees = models.ManyToManyField(User, related_name='attended_meetings')  # For agency users
    company_contacts = models.ManyToManyField(Contact, related_name='meetings_attended')  # For company contacts

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} - {self.date}"

    class Meta:
        ordering = ['-date', '-time']
