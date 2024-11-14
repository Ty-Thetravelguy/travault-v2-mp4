from django import forms
from .models import Ticket, TicketSubject
from agencies.models import CustomUser
from crm.models import Company, Contact


class TicketForm(forms.ModelForm):
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))

    CATEGORY_CHOICES_CLIENT = [
        ('complaint', 'Complaint'),
        ('query', 'Query'),
        ('request', 'Request'),
    ]
    
    CATEGORY_CHOICES_AGENCY = [
        ('consultant_error', 'Consultant Error'),
        ('supplier_error', 'Supplier Error'),
        ('supplier_query', 'Supplier Query'),
        ('system_error', 'System Error'),
        ('system_query', 'System Query'),
        ('system_enhancement', 'System Enhancement'),
    ]

    category = forms.ChoiceField(
        choices=[], 
        required=False,
        widget=forms.Select(attrs={'class': 'category-field form-select'})
    )

    assigned_to = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    company = forms.ModelChoiceField(
        queryset=Company.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    contact = forms.ModelChoiceField(
        queryset=Contact.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    
    class Meta:
        model = Ticket
        fields = ['company', 'contact', 'priority', 'subject', 'description', 'category_type', 'category', 'assigned_to']

    def __init__(self, *args, **kwargs):
        self.agency = kwargs.pop('agency', None)
        super().__init__(*args, **kwargs)
    
        if self.agency:
            self.fields['company'].queryset = Company.objects.filter(agency=self.agency)
            self.fields['assigned_to'].queryset = CustomUser.objects.filter(agency=self.agency)

        # Get company_id from either initial data or POST data
        company_id = None
        if 'company' in self.data:
            try:
                company_id = int(self.data['company'])
            except (ValueError, TypeError):
                pass
        elif self.initial.get('company'):
            company_id = self.initial.get('company')

        # Filter contacts based on company_id
        if company_id:
            try:
                self.fields['contact'].queryset = Contact.objects.filter(company_id=company_id)
            except (ValueError, TypeError):
                self.fields['contact'].queryset = Contact.objects.none()
        else:
            self.fields['contact'].queryset = Contact.objects.none()
        
        # Get category_type from self.data first, then instance, then initial
        if 'category_type' in self.data:
            category_type = self.data.get('category_type')
        elif self.instance and self.instance.pk:
            category_type = self.instance.category_type
        else:
            category_type = self.initial.get('category_type')

        if category_type == 'client':
            self.fields['category'].choices = self.CATEGORY_CHOICES_CLIENT
        elif category_type == 'agency':
            self.fields['category'].choices = self.CATEGORY_CHOICES_AGENCY
        else:
            self.fields['category'].choices = []

        # Set the initial value for the category
        if self.instance and self.instance.pk:
            self.fields['category'].initial = self.instance.category

        # If company is provided initially, make the field read-only
        if self.initial.get('company'):
            self.fields['company'].widget.attrs['readonly'] = True

        # Populate assigned_to queryset based on agency
        if self.agency:
            self.fields['assigned_to'].queryset = CustomUser.objects.filter(agency=self.agency)

        # Ensure the category field is enabled if choices are available
        if category_type in ['client', 'agency']:
            self.fields['category'].widget.attrs.pop('disabled', None)
        else:
            self.fields['category'].widget.attrs['disabled'] = 'disabled'

    # Indent the clean_category method inside the class
    def clean_category(self):
        category = self.cleaned_data.get('category')
        category_type = self.cleaned_data.get('category_type')

        # Validate category based on category_type
        if category_type == 'client' and category not in dict(self.CATEGORY_CHOICES_CLIENT):
            raise forms.ValidationError("Invalid category for client type.")
        elif category_type == 'agency' and category not in dict(self.CATEGORY_CHOICES_AGENCY):
            raise forms.ValidationError("Invalid category for agency type.")
        
        return category

    # Indent the clean_subject method inside the class
    def clean_subject(self):
        subject_text = self.cleaned_data['subject']
        subject, _ = TicketSubject.objects.get_or_create(subject=subject_text)
        return subject
