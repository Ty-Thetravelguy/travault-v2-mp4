# crm/forms.py
from django import forms
from .models import Company, Contact
from django.contrib.auth import get_user_model

User = get_user_model()

class CompanyForm(forms.ModelForm):

    linked_companies = forms.ModelMultipleChoiceField(
        queryset=Company.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'display: none;'}),
    )

    class Meta:
        model = Company
        fields = [
            'company_name',         
            'street_address',
            'city',
            'state_province',
            'postal_code',
            'country',
            'phone_number', 
            'email',
            'description',
            'linkedin_social_page',
            'industry',
            'company_type',
            'company_owner',
            'ops_team',
            'client_type',
            'account_status',
            'linked_companies',
        ]
        widgets = {
            'company_type': forms.Select(attrs={'class': 'form-control'}),
            'company_owner': forms.Select(attrs={'class': 'form-control'}),
            'client_type': forms.Select(attrs={'class': 'form-control'}),
            'account_status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        agency = kwargs.pop('agency', None)
        super().__init__(*args, **kwargs)
        if agency:
            self.fields['linked_companies'].queryset = Company.objects.filter(agency=agency).exclude(id=self.instance.id)
            self.fields['company_owner'].queryset = User.objects.filter(
                agency=agency,
                user_type__in=['admin', 'sales']
            )


class ContactForm(forms.ModelForm):
    is_primary_contact = forms.BooleanField(required=False, label="Is Primary Contact")
    is_travel_booker_contact = forms.BooleanField(required=False, label="Is a Travel Booker")
    is_traveller_contact = forms.BooleanField(required=False, label="Is a Traveller")
    is_vip_traveller_contact = forms.BooleanField(required=False, label="VIP")
    department = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'phone', 'mobile', 'job_title', 'department', 
                  'is_primary_contact', 'is_travel_booker_contact', 'is_traveller_contact', 'is_vip_traveller_contact', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field in ['is_primary_contact', 'is_travel_booker_contact', 'is_traveller_contact','is_vip_traveller_contact']:
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-control'})