#activity_log/forms.py

from django import forms
from .models import Meeting
from crm.models import Contact
from django.contrib.auth import get_user_model

User = get_user_model()

class MeetingForm(forms.ModelForm):
    attendees_input = forms.CharField(required=False, widget=forms.HiddenInput())
    to_do_task_message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your follow-up message here...'})
    )  

    class Meta:
        model = Meeting
        fields = [
            'subject', 'outcome', 'location', 'date', 'time',
            'duration', 'details', 'to_do_task_date', 'to_do_task_message', 'attendees_input'
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
            'to_do_task_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}), 
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

            # Schedule the email if to_do_task_date is set
            if meeting.to_do_task_date and meeting.to_do_task_message:
                # Combine date with a default time (e.g., 09:00 AM)
                task_datetime = timezone.make_aware(
                    timezone.datetime.combine(meeting.to_do_task_date, timezone.time(9, 0)),
                    timezone.get_current_timezone()
                )
                now = timezone.now()
                delay = (task_datetime - now).total_seconds()

                if delay > 0:
                    send_follow_up_email.apply_async((meeting.id,), eta=task_datetime)
                    print(f"Scheduled follow-up email for meeting '{meeting.subject}' at {task_datetime}")
                else:
                    # If the date is in the past or now, send immediately
                    send_follow_up_email.delay(meeting.id)
                    print(f"Sent follow-up email immediately for meeting '{meeting.subject}'")
        return meeting