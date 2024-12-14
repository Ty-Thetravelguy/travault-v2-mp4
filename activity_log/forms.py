import logging
from datetime import datetime, time
from django import forms
from .models import Meeting, Call, Email
from crm.models import Contact
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, time  
from .tasks import send_follow_up_email 

User = get_user_model()

class MeetingForm(forms.ModelForm):
    """
    A form for creating and updating meetings. 
    It includes fields for meeting details, attendees, and follow-up tasks.
    """
    attendees_input = forms.CharField(required=False, widget=forms.HiddenInput())
    to_do_task_message = forms.CharField(
        required=False,
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
        """
        Initializes the form with company and creator information.
        """
        self.company = kwargs.pop('company', None)
        self.creator = kwargs.pop('creator', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Saves the meeting instance, linking it to the company and creator.
        If attendees are provided, they are added to the meeting.
        If a follow-up task is set, it schedules an email reminder.
        """
        meeting = super().save(commit=False)
        if self.company:
            meeting.company = self.company  # Ensure the meeting is linked to the correct company
        if self.creator:
            meeting.creator = self.creator  # Set the creator

        if commit:
            meeting.save()

            # Process attendees_input to add to attendees and company_contacts
            attendees_data = self.cleaned_data.get('attendees_input', '')

            if attendees_data:
                attendees_ids = attendees_data.split(',')

                for attendee_id in attendees_ids:
                    if attendee_id.startswith('contact_user_'):
                        try:
                            user_id = int(attendee_id.replace('contact_user_', ''))
                            user = User.objects.get(id=user_id)
                            meeting.attendees.add(user)
                        except (ValueError, User.DoesNotExist):
                            # Log error or handle it as needed
                            pass
                    elif attendee_id.startswith('contact_contact_'):
                        try:
                            contact_id = int(attendee_id.replace('contact_contact_', ''))
                            contact = Contact.objects.get(id=contact_id)
                            meeting.company_contacts.add(contact)
                        except (ValueError, Contact.DoesNotExist):
                            # Log error or handle it as needed
                            pass

            # Schedule the email if to_do_task_date is set
            if meeting.to_do_task_date and meeting.to_do_task_message:
                # Combine date with a default time (e.g., 09:00 AM)
                task_datetime = timezone.make_aware(
                    datetime.combine(meeting.to_do_task_date, time(9, 0)),
                    timezone.get_current_timezone()
                )
                now = timezone.now()
                delay = (task_datetime - now).total_seconds()

                if delay > 0:
                    send_follow_up_email.apply_async((meeting.id,), eta=task_datetime)
                else:
                    # If the date is in the past or now, send immediately
                    send_follow_up_email.delay(meeting.id)

        return meeting


class CallForm(forms.ModelForm):
    """
    A form for creating and updating calls. 
    It includes fields for call details and follow-up tasks.
    """
    contacts_input = forms.CharField(widget=forms.HiddenInput(), required=False)
    to_do_task_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your follow-up message here...'})
    )
    
    class Meta:
        model = Call
        fields = ['subject', 'outcome', 'date', 'time', 'duration', 'details', 'to_do_task_date', 'to_do_task_message']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'to_do_task_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'duration': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initializes the form with company and creator information.
        """
        self.company = kwargs.pop('company', None)
        self.creator = kwargs.pop('creator', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Saves the call instance, linking it to the company and creator.
        If contacts are provided, they are added to the call.
        If a follow-up task is set, it schedules an email reminder.
        """
        call = super().save(commit=False)
        call.company = self.company
        call.creator = self.creator
        if commit:
            call.save()
            contacts_input = self.cleaned_data.get('contacts_input', '')
            if contacts_input:
                contact_ids = contacts_input.split(',')
                contacts = Contact.objects.filter(id__in=contact_ids)
                call.contacts.set(contacts)
            self.save_m2m()
            
            # Schedule the email if to_do_task_date is set
            if call.to_do_task_date and call.to_do_task_message:
                task_datetime = timezone.make_aware(
                    datetime.combine(call.to_do_task_date, time(9, 0)),
                    timezone.get_current_timezone()
                )
                now = timezone.now()
                delay = (task_datetime - now).total_seconds()

                if delay > 0:
                    send_follow_up_email.apply_async((call.id,), eta=task_datetime)
                else:
                    send_follow_up_email.delay(call.id)
        return call


class EmailForm(forms.ModelForm):
    """
    A form for creating and updating emails. 
    It includes fields for email details and follow-up tasks.
    """
    contacts_input = forms.CharField(widget=forms.HiddenInput(), required=False)
    to_do_task_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your follow-up message here...'})
    )
    
    class Meta:
        model = Email
        fields = ['subject', 'outcome', 'date', 'time', 'details', 'to_do_task_date', 'to_do_task_message']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'to_do_task_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initializes the form with company and creator information.
        """
        self.company = kwargs.pop('company', None)
        self.creator = kwargs.pop('creator', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Saves the email instance, linking it to the company and creator.
        If contacts are provided, they are added to the email.
        If a follow-up task is set, it schedules an email reminder.
        """
        email = super().save(commit=False)
        email.company = self.company
        email.creator = self.creator
        if commit:
            email.save()
            contacts_input = self.cleaned_data.get('contacts_input', '')
            if contacts_input:
                contact_ids = contacts_input.split(',')
                contacts = Contact.objects.filter(id__in=contact_ids)
                email.contacts.set(contacts)
            self.save_m2m()
            
            # Schedule the email if to_do_task_date is set
            if email.to_do_task_date and email.to_do_task_message:
                task_datetime = timezone.make_aware(
                    datetime.combine(email.to_do_task_date, time(9, 0)),
                    timezone.get_current_timezone()
                )
                now = timezone.now()
                delay = (task_datetime - now).total_seconds()

                if delay > 0:
                    send_follow_up_email.apply_async((email.id,), eta=task_datetime)
                else:
                    send_follow_up_email.delay(email.id)
        return email
