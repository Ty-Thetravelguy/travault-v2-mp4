# crm/forms.py

from django import forms
from .models import Company, Contact, CompanyNotes, TransactionFee
from django.contrib.auth import get_user_model

User = get_user_model()

class CompanyForm(forms.ModelForm):
    """
    Form for creating and updating Company instances.

    This form includes fields for the company's details, including name, address,
    contact information, type, and linked companies. It also provides dynamic 
    filtering of linked companies and company owners based on the user's agency.

    Fields:
        - company_name: Name of the company.
        - street_address, city, state_province, postal_code, country: Address details.
        - phone_number: Primary contact number for the company.
        - email: Primary email address for the company.
        - description: A brief description of the company.
        - linkedin_social_page: LinkedIn page URL of the company.
        - industry: The industry in which the company operates.
        - company_type: Type of the company, selectable from a list.
        - company_owner: The user responsible for the company, filtered by agency.
        - ops_team: Operational team assigned to the company.
        - client_type: The client type, selectable from predefined choices.
        - account_status: Current account status of the company.
        - linked_companies: Other companies linked to this company, filtered by agency.
    """

    linked_companies = forms.ModelMultipleChoiceField(
        queryset=Company.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'display: none;'}),
        help_text="Select linked companies relevant to this company."
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
        """
        Initializes the form with the given arguments, filtering linked companies 
        and company owners based on the user's agency.

        Args:
            agency (Agency): The agency object used to filter linked companies and owners.
        """
        agency = kwargs.pop('agency', None)
        super().__init__(*args, **kwargs)
        if agency:
            # Filter linked companies based on the user's agency and exclude the current instance
            self.fields['linked_companies'].queryset = Company.objects.filter(agency=agency).exclude(id=self.instance.id)
            # Filter company owners based on the user's agency and specific user types
            self.fields['company_owner'].queryset = User.objects.filter(
                agency=agency,
                user_type__in=['admin', 'sales']
            )


class ContactForm(forms.ModelForm):
    """
    Form for creating and updating Contact instances.

    Includes fields for personal and contact details, as well as attributes 
    that define the contact's roles within the company (e.g., primary contact, traveller).

    Fields:
        - first_name, last_name: Name of the contact.
        - email, phone, mobile: Contact details.
        - job_title: The contact's job title within the company.
        - department: The department in which the contact works.
        - is_primary_contact: Whether this contact is the primary contact for the company.
        - is_travel_booker_contact: Whether this contact is responsible for booking travel.
        - is_traveller_contact: Whether this contact is a traveller.
        - is_vip_traveller_contact: Whether this contact is a VIP traveller.
        - notes: Additional notes about the contact.
    """

    is_primary_contact = forms.BooleanField(required=False, label="Is Primary Contact")
    is_travel_booker_contact = forms.BooleanField(required=False, label="Is a Travel Booker")
    is_traveller_contact = forms.BooleanField(required=False, label="Is a Traveller")
    is_vip_traveller_contact = forms.BooleanField(required=False, label="VIP")
    department = forms.CharField(max_length=100, required=False, help_text="Enter the department of the contact.")

    class Meta:
        model = Contact
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'mobile', 'job_title', 'department', 
            'is_primary_contact', 'is_travel_booker_contact', 'is_traveller_contact', 'is_vip_traveller_contact', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Initializes the form with the given arguments, updating the widget classes
        for checkbox and text input fields for consistent styling.
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            # Update class for checkbox fields
            if field in ['is_primary_contact', 'is_travel_booker_contact', 'is_traveller_contact','is_vip_traveller_contact']:
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})
            else:
                # Update class for all other fields
                self.fields[field].widget.attrs.update({'class': 'form-control'})


class CompanyNotesForm(forms.ModelForm):
    """
    Form for creating and updating CompanyNotes instances.

    Excludes fields that are automatically managed (e.g., company reference and timestamps).

    Fields include various types of notes and policy descriptions relevant to the company.
    """

    class Meta:
        model = CompanyNotes
        exclude = ['company', 'last_updated', 'updated_by']
        widgets = {
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'fop_limit': forms.TextInput(attrs={'class': 'form-control'}),
            'invoice_references': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'corporate_hotel_rates': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'corporate_airline_fares': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'company_memberships': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'travel_policy': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'flight_notes': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'accommodation_notes': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'car_hire_notes': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'transfer_notes': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'rail_notes': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'other_notes': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }

class TransactionFeeForm(forms.ModelForm):
    """
    Form for creating and updating TransactionFee instances.

    Fields:
        - service: Name of the service associated with the fee.
        - online_fee: Fee amount for online transactions.
        - offline_fee: Fee amount for offline transactions.
    """

    class Meta:
        model = TransactionFee
        fields = ['service', 'online_fee', 'offline_fee']