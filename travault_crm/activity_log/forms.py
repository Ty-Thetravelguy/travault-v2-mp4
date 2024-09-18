#activity_log/forms.py

from django import forms
from .models import Meeting
from crm.models import Contact
from django.contrib.auth import get_user_model

User = get_user_model()

class MeetingForm(forms.ModelForm):
    attendees_input = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Meeting
        fields = [
            'subject', 'outcome', 'location', 'date', 'time',
            'duration', 'details', 'to_do_task_date', 'attendees_input'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'to_do_task_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'duration': forms.Select(attrs={'class': 'form-control'}),
            'outcome': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'details': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)  # Company context passed from view
        super().__init__(*args, **kwargs)
        # No need to set queryset for attendees; handled via JavaScript and hidden field

    def save(self, commit=True):
        meeting = super().save(commit=False)
        meeting.company = self.company  # Ensure the meeting is linked to the correct company
        if commit:
            meeting.save()
            # Process attendees_input to add to attendees and company_contacts
            attendees_data = self.cleaned_data.get('attendees_input', '')
            if attendees_data:
                attendees_ids = attendees_data.split(',')
                for attendee_id in attendees_ids:
                    if attendee_id.startswith('user_'):
                        user_id = int(attendee_id.replace('user_', ''))
                        user = User.objects.get(id=user_id)
                        meeting.attendees.add(user)
                    elif attendee_id.startswith('contact_'):
                        contact_id = int(attendee_id.replace('contact_', ''))
                        contact = Contact.objects.get(id=contact_id)
                        meeting.company_contacts.add(contact)
            meeting.save()
        return meeting