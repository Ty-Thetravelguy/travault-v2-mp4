from django import forms
from .models import Meeting
from crm.models import Company, Contact
from django_ckeditor_5.widgets import CKEditor5Widget

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = [
            'subject',
            'attendees',
            'outcome',
            'location',
            'date',
            'time',
            'duration',
            'details',  # Ensure 'details' is included
            'to_do_task_date',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'to_do_task_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'duration': forms.Select(attrs={'class': 'form-control'}),
            'outcome': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'attendees': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'details': CKEditor5Widget(config_name='default'),  # Use CKEditor5Widget
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        agency = kwargs.pop('agency', None)
        super().__init__(*args, **kwargs)
        if company:
            # Limit attendees to contacts from the company and linked companies
            linked_companies = company.linked_companies.all()
            companies = [company] + list(linked_companies)
            self.fields['attendees'].queryset = Contact.objects.filter(company__in=companies)
        else:
            self.fields['attendees'].queryset = Contact.objects.none()
