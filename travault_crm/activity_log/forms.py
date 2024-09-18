# activity_log/forms.py
from django import forms
from .models import Meeting
from crm.models import Contact
from django.contrib.auth import get_user_model

User = get_user_model()

class MeetingForm(forms.ModelForm):
    # Attendees fields
    company_contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.none(),  # Empty queryset initially, will be filtered later
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )
    agency_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Meeting
        fields = [
            'subject', 'outcome', 'location', 'date', 'time',
            'duration', 'details', 'to_do_task_date', 'company_contacts', 'agency_users'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'duration': forms.Select(attrs={'class': 'form-control'}),
            'outcome': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'details': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)  # Pop the company from the kwargs
        super().__init__(*args, **kwargs)
        # Set the queryset for the company contacts based on the current company
        if company:
            self.fields['company_contacts'].queryset = Contact.objects.filter(company=company)