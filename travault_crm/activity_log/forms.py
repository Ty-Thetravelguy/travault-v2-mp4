#activity_log/forms.py

from django import forms
from .models import ActivityLog

class ActivityLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['activity_type', 'subject', 'description', 'related_contact']

class CallLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['subject', 'description', 'related_contact']

class EmailLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['subject', 'description', 'related_contact']

class MeetingLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['subject', 'description', 'related_contact']

class TicketForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['subject', 'description', 'related_contact']

class DealForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['subject', 'description', 'related_contact']