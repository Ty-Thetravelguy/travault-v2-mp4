# agencies/forms.py

from django import forms
from allauth.account.forms import SignupForm
from allauth.account.models import EmailAddress 
from .models import Agency, CustomUser
import re
import logging

logger = logging.getLogger(__name__)

class AgencyRegistrationForm(SignupForm):
    """
    Form for registering a new agency, extending the allauth SignupForm.

    Fields:
        - company_name: The name of the agency.
        - company_address: The full address of the agency, expecting up to 6 lines.
        - vat_number: The VAT number of the agency, must be exactly 9 digits.
        - company_reg_number: The company registration number, either 8 digits or 2 letters followed by 6 digits.
        - phone_number: The contact phone number for the agency.
        - contact_full_name: The full name of the primary contact person.
        - employees: The size range of the agency in terms of employees.
        - business_focus: The main business focus of the agency.
        - agree_terms: Checkbox to agree to the terms and conditions.
    """

    company_name = forms.CharField(max_length=100, required=True)
    company_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6}),
        required=True,
        help_text="Enter your address, with each line separated by a newline character. Please provide up to 6 lines."
    )
    vat_number = forms.CharField(max_length=9, required=True, label="VAT Number")
    company_reg_number = forms.CharField(max_length=8, required=True, label="Company Registration Number")
    phone_number = forms.CharField(max_length=20, required=True)
    contact_full_name = forms.CharField(max_length=100, required=True, label="Primary Contact Full Name",
                                        help_text="Enter the full name (first and last name) of the primary contact.")
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
    agree_terms = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and orders fields as specified.
        """
        super(AgencyRegistrationForm, self).__init__(*args, **kwargs)
        # Reorder the fields exactly as specified
        field_order = [
            'company_name', 'company_address', 'vat_number', 'company_reg_number', 'phone_number',
            'contact_full_name', 'email', 'email2', 'username', 'employees', 'business_focus',
            'password1', 'password2', 'agree_terms'
        ]
        self.order_fields(field_order)

    def clean_username(self):
        """
        Validates that the username is unique.

        Raises:
            ValidationError: If a user with the same username already exists.

        Returns:
            str: Cleaned data for the username field.
        """
        print("DEBUG: Validating username")
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_company_name(self):
        """
        Validates the company name to ensure it is unique.

        Raises:
            ValidationError: If a company with the same name already exists.

        Returns:
            str: Cleaned data for the company_name field.
        """
        company_name = self.cleaned_data.get('company_name')
        if Agency.objects.filter(agency_name=company_name).exists():  # Corrected field name
            raise forms.ValidationError("A company with this name already exists.")
        return company_name

    def clean_vat_number(self):
        """
        Validates the VAT number to ensure it is exactly 9 digits and unique.

        Raises:
            ValidationError: If the VAT number is not 9 digits or already exists.

        Returns:
            str: Cleaned data for the vat_number field.
        """
        vat_number = self.cleaned_data.get('vat_number')
        if not vat_number.isdigit() or len(vat_number) != 9:
            raise forms.ValidationError("VAT number must be exactly 9 digits.")
        if Agency.objects.filter(vat_number=vat_number).exists():
            raise forms.ValidationError("A company with this VAT number already exists.")
        return vat_number

    def clean_company_reg_number(self):
        """
        Validates the company registration number to match expected formats and uniqueness.

        Raises:
            ValidationError: If the registration number does not match the pattern or already exists.

        Returns:
            str: Cleaned data for the company_reg_number field.
        """
        reg_number = self.cleaned_data.get('company_reg_number')
        if not re.match(r'^\d{8}$|^[A-Z]{2}\d{6}$', reg_number):
            raise forms.ValidationError("Company registration number must be 8 digits or 2 letters followed by 6 digits.")
        if Agency.objects.filter(company_reg_number=reg_number).exists():
            raise forms.ValidationError("A company with this registration number already exists.")
        return reg_number

    def clean_company_address(self):
        """
        Validates the company address to ensure it does not exceed 6 lines.

        Raises:
            ValidationError: If the address exceeds 6 lines.

        Returns:
            str: Cleaned data for the company_address field.
        """
        address = self.cleaned_data.get('company_address')
        lines = [line for line in address.split('\n') if line.strip()]  # Ignore empty lines
        if len(lines) > 6:
            raise forms.ValidationError("Please provide up to 6 lines for the address.")
        return address

    def save(self, request):
        print("DEBUG: Entering save method of AgencyRegistrationForm.")
        try:
            # Create user
            print(f"DEBUG: Attempting to create user with username: {self.cleaned_data.get('username')}")
            user = super(AgencyRegistrationForm, self).save(request)
            print(f"DEBUG: User created successfully with email: {user.email}")

            # Attempt to create agency
            try:
                agency_data = {
                    "agency_name": self.cleaned_data['company_name'],
                    "address": self.cleaned_data['company_address'],
                    "phone": self.cleaned_data['phone_number'],
                    "email": user.email,
                    "vat_number": self.cleaned_data['vat_number'],
                    "company_reg_number": self.cleaned_data['company_reg_number'],
                    "employees": self.cleaned_data['employees'],
                    "business_focus": self.cleaned_data['business_focus'],
                    "contact_name": self.cleaned_data['contact_full_name'],
                }
                print("DEBUG: Data for agency creation:", agency_data)

                agency = Agency.objects.create(**agency_data)
                print(f"DEBUG: Agency created successfully: {agency.agency_name}")
            except Exception as e:
                print(f"DEBUG ERROR: Exception during agency creation: {e}")
                if 'user' in locals():
                    user.delete()
                    print("DEBUG: User deleted due to agency creation failure")
                import traceback
                traceback.print_exc()  # Print full traceback for deeper insight
                raise

            # Update user with agency details
            try:
                full_name = self.cleaned_data['contact_full_name'].strip().split()
                if full_name:
                    user.first_name = full_name[0]
                    user.last_name = ' '.join(full_name[1:]) if len(full_name) > 1 else ''
                user.user_type = 'admin'
                user.agency = agency
                user.save()
                print(f"DEBUG: User linked to agency: {agency.agency_name}")
            except Exception as e:
                print(f"DEBUG ERROR: Exception during user update: {e}")
                if agency:
                    agency.delete()
                    print(f"DEBUG: Agency deleted: {agency.agency_name}")
                raise

            return user

        except Exception as e:
            print(f"DEBUG ERROR: Unexpected exception in save method: {e}")
            raise


class UserForm(forms.ModelForm):
    """
    Form for creating and updating CustomUser instances.

    Fields:
        - username: The username for the user.
        - email: The email address of the user.
        - first_name: The first name of the user.
        - last_name: The last name of the user.
        - user_type: The type of user (e.g., admin, agent).
    """
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

    def clean_email(self):
        """
        Validate that the email is not already in use by another user.
        """
        email = self.cleaned_data.get('email')
        user_id = self.instance.id if self.instance else None

        # Check if email exists for another user
        if CustomUser.objects.filter(email=email).exclude(id=user_id).exists():
            raise forms.ValidationError("This email address is already in use. Please use a different email.")

        # Check if email exists in EmailAddress model
        if EmailAddress.objects.filter(email=email).exclude(user=self.instance).exists():
            raise forms.ValidationError("This email address is already registered. Please use a different email.")

        return email


class AgencyProfileForm(forms.ModelForm):
    """
    Form for updating an Agency's profile.
    """
    class Meta:
        model = Agency
        fields = ['agency_name', 'address', 'vat_number', 'company_reg_number', 'phone', 'email', 'employees', 'business_focus', 'contact_name']
        labels = {
            'agency_name': 'Agency Name',
            'address': 'Business Address',
            'vat_number': 'VAT Number',
            'company_reg_number': 'Company Registration Number',
            'phone': 'Phone Number',
            'email': 'Email Address',
            'employees': 'Number of Employees',
            'business_focus': 'Business Focus',
            'contact_name': 'Primary Contact Name'
        }
        widgets = {
            'agency_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'vat_number': forms.TextInput(attrs={'class': 'form-control'}),
            'company_reg_number': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'employees': forms.Select(attrs={'class': 'form-control'}),
            'business_focus': forms.Select(attrs={'class': 'form-control'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    field_order = ['agency_name', 'address', 'vat_number', 'company_reg_number', 'contact_name', 'phone', 'email', 'employees', 'business_focus']
