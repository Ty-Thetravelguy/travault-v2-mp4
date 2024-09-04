# agencies/forms.py

from django import forms
from allauth.account.forms import SignupForm
from .models import Agency, CustomUser
import re

class AgencyRegistrationForm(SignupForm):
    company_name = forms.CharField(max_length=100, required=True)
    company_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6}),
        required=True,
        help_text="Enter your address, with each line separated by a newline character. Please provide 6 lines."
    )
    vat_number = forms.CharField(max_length=9, required=True, label="VAT Number")
    company_reg_number = forms.CharField(max_length=8, required=True, label="Company Registration Number")
    phone_number = forms.CharField(max_length=20, required=True)
    contact_full_name = forms.CharField(max_length=100, required=True, label="Primary Contact Full Name",
                                        help_text="Enter the full name (first and last name) of the primary contact.")
    # email and username are already included in SignupForm
    employees = forms.ChoiceField(choices=[
        ('', 'Select range'),
        ('1-10', '1-10'),
        ('11-50', '11-50'),
        ('51-100', '51-100'),
        ('100+', '100+')
    ], required=True)
    business_focus = forms.ChoiceField(choices=[
        ('', 'Select focus'),
        ('corporate', 'Corporate Travel'),
        ('leisure', 'Leisure Travel'),
        ('mixed', 'Mixed')
    ], required=True)
    # password1 and password2 are already included in SignupForm
    agree_terms = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Reorder the fields exactly as specified
        field_order = [
            'company_name', 'company_address', 'vat_number', 'company_reg_number', 'phone_number',
            'contact_full_name', 'email', 'email2', 'username', 'employees', 'business_focus',
            'password1', 'password2', 'agree_terms'
        ]
        self.order_fields(field_order)

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if Agency.objects.filter(name=company_name).exists():
            raise forms.ValidationError("A company with this name already exists.")
        return company_name

    def clean_vat_number(self):
        vat_number = self.cleaned_data.get('vat_number')
        if not vat_number.isdigit() or len(vat_number) != 9:
            raise forms.ValidationError("VAT number must be exactly 9 digits.")
        if Agency.objects.filter(vat_number=vat_number).exists():
            raise forms.ValidationError("A company with this VAT number already exists.")
        return vat_number

    def clean_company_reg_number(self):
        reg_number = self.cleaned_data.get('company_reg_number')
        if not re.match(r'^\d{8}$|^[A-Z]{2}\d{6}$', reg_number):
            raise forms.ValidationError("Company registration number must be 8 digits or 2 letters followed by 6 digits.")
        if Agency.objects.filter(company_reg_number=reg_number).exists():
            raise forms.ValidationError("A company with this registration number already exists.")
        return reg_number

    def clean_company_address(self):
        address = self.cleaned_data.get('company_address')
        lines = [line for line in address.split('\n') if line.strip()]  # Ignore empty lines
        if len(lines) > 6:
            raise forms.ValidationError("Please provide up to 6 lines for the address.")
        return address

    def save(self, request):
        user = super(AgencyRegistrationForm, self).save(request)
        
        # Split the full name into first and last name
        full_name = self.cleaned_data['contact_full_name'].split()
        if len(full_name) > 1:
            user.first_name = full_name[0]
            user.last_name = ' '.join(full_name[1:])
        else:
            user.first_name = full_name[0]
            user.last_name = ''
        
        # Setting user role
        if request.user.is_authenticated and request.user.user_type == 'admin':
            user.user_type = 'agent'
        else:
            user.user_type = 'admin'
        
        # Save the user with updated names and role
        user.save()
        
        # Create the agency linked to the user
        address_lines = self.cleaned_data['company_address'].split('\n')
        agency = Agency.objects.create(
            name=self.cleaned_data['company_name'],
            address='\n'.join(address_lines),
            phone=self.cleaned_data['phone_number'],
            email=user.email,
            vat_number=self.cleaned_data['vat_number'],
            company_reg_number=self.cleaned_data['company_reg_number'],
            employees=self.cleaned_data['employees'],
            business_focus=self.cleaned_data['business_focus'],
            contact_name=self.cleaned_data['contact_full_name']
        )
        
        # Link the agency to the user
        user.agency = agency
        user.save()
        
        return user

class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'user_type']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}), 
        }
