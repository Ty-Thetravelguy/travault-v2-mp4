# activity_log/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from crm.models import Company

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
    attendees = GenericRelation('MeetingAttendee', related_query_name='meetings')
    associated_companies = models.ManyToManyField(Company, related_name='meetings')
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES)
    date = models.DateField()
    time = models.TimeField()
    duration = models.IntegerField(choices=DURATION_CHOICES)
    
    # Change CKEditor5Field to a TextField
    details = models.TextField('Details', default='')  
    
    to_do_task_date = models.DateField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings')
    agency = models.ForeignKey('agencies.Agency', on_delete=models.CASCADE, related_name='meetings')  # Ensure agency field is added
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} - {self.date}"

    class Meta:
        ordering = ['-date', '-time']

class MeetingAttendee(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='meeting_attendees')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    attendee_object = GenericForeignKey('content_type', 'object_id')
