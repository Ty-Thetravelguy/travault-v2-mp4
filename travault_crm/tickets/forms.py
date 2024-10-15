from django import forms
from .models import Ticket, TicketSubject
from agencies.models import CustomUser


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
    
    class Meta:
        model = Ticket
        fields = ['company', 'contact', 'priority', 'subject', 'description', 'category_type', 'category', 'assigned_to']

    def __init__(self, *args, **kwargs):
        self.agency = kwargs.pop('agency', None)
        super(TicketForm, self).__init__(*args, **kwargs)
        
        # Determine the category_type and set choices
        if self.instance and self.instance.pk:
            # Editing an existing ticket
            category_type = self.instance.category_type
        else:
            # Creating a new ticket or handling form submission
            category_type = self.data.get('category_type') or self.initial.get('category_type')

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

    def clean_category(self):
        category = self.cleaned_data.get('category')
        category_type = self.cleaned_data.get('category_type')

        # Validate category based on category_type
        if category_type == 'client' and category not in dict(self.CATEGORY_CHOICES_CLIENT):
            raise forms.ValidationError("Invalid category for client type.")
        elif category_type == 'agency' and category not in dict(self.CATEGORY_CHOICES_AGENCY):
            raise forms.ValidationError("Invalid category for agency type.")
        
        return category

    def clean_subject(self):
        subject_text = self.cleaned_data['subject']
        subject, _ = TicketSubject.objects.get_or_create(subject=subject_text)
        return subject