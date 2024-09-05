# crm/forms.py

from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'company_name',         # 1. Company name
            'company_address',      # 2. Company address
            'email',                # 3. Email
            'description',          # 4. Description
            'linkedin_social_page', # 5. Linkedin social page
            'industry',             # 6. Industry
            'company_type',         # 7. Company type
            'company_owner',        # 8. Company owner
            'ops_team',             # 9. Ops team
            'client_type',          # 10. Client type
            'account_status'        # 11. Account status
        ]
        widgets = {
            'company_type': forms.Select(attrs={'class': 'form-control'}),
            'company_owner': forms.Select(attrs={'class': 'form-control'}),
            'client_type': forms.Select(attrs={'class': 'form-control'}),
            'account_status': forms.Select(attrs={'class': 'form-control'}),
        }