# activity_log/forms.py

from django import forms
from django.contrib.contenttypes.models import ContentType
from .models import Meeting, MeetingAttendee
from crm.models import Company, Contact
from django.contrib.auth import get_user_model

User = get_user_model()

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            'subject', 'outcome', 'location', 'date', 'time',
            'duration', 'details', 'to_do_task_date'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'to_do_task_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'duration': forms.Select(attrs={'class': 'form-control'}),
            'outcome': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)  # Remove 'company' from kwargs
        self.agency = kwargs.pop('agency', None)    # Remove 'agency' from kwargs
        super().__init__(*args, **kwargs)

