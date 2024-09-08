# crm/forms.py
from django import forms
from .models import Company
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
            'account_status'
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