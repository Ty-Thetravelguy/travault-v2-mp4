from django import forms
from .models import AgentSupportSupplier

class AgentSupportSupplierForm(forms.ModelForm):
    # Existing fields
    agent_websites = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        help_text="Enter multiple websites separated by commas if you have more than one.",
        required=False
    )
    contact_numbers = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        help_text="Enter multiple numbers separated by commas if you have more than one.",
        required=False
    )
    group_email = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        help_text="Enter multiple emails separated by commas if you have more than one.",
        required=False
    )
    general_email = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        help_text="Enter multiple emails separated by commas if you have more than one.",
        required=False
    )
    other = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        required=False
    )

    # New process fields
    process_1_subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    process_1_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )
    process_2_subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    process_2_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )
    process_3_subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    process_3_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )
    process_4_subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    process_4_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = AgentSupportSupplier
        fields = ['supplier_type', 'supplier_name', 'agent_websites', 'contact_numbers', 
                  'group_email', 'general_email', 'account_manager', 'account_manager_contact', 
                  'account_manager_email', 'other', 
                  'process_1_subject', 'process_1_text', 
                  'process_2_subject', 'process_2_text',
                  'process_3_subject', 'process_3_text',
                  'process_4_subject', 'process_4_text']
        widgets = {
            'supplier_type': forms.Select(attrs={'class': 'form-control'}),
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_manager': forms.TextInput(attrs={'class': 'form-control'}),
            'account_manager_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'account_manager_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
