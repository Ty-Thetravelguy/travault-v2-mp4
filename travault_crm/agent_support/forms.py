#agent_support/forms.py

from django import forms
from .models import AgentSupportSupplier
from django.core.exceptions import ValidationError


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
    process_1_pdf = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        help_text="Upload a PDF file for Process 1"
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
    process_2_pdf = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        help_text="Upload a PDF file for Process 2"
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
    process_3_pdf = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        help_text="Upload a PDF file for Process 3"
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
    process_4_pdf = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        help_text="Upload a PDF file for Process 4"
    )


    class Meta:
            model = AgentSupportSupplier
            fields = [
                'supplier_type', 'supplier_name', 'agent_websites', 'contact_numbers', 
                'group_email', 'general_email', 'account_manager', 'account_manager_contact', 
                'account_manager_email', 'other', 
                'process_1_subject', 'process_1_text', 'process_1_pdf', 
                'process_2_subject', 'process_2_text', 'process_2_pdf', 
                'process_3_subject', 'process_3_text', 'process_3_pdf', 
                'process_4_subject', 'process_4_text', 'process_4_pdf'
            ]

    def clean_process_1_pdf(self):
        return self.clean_pdf('process_1_pdf')

    def clean_process_2_pdf(self):
        return self.clean_pdf('process_2_pdf')

    def clean_process_3_pdf(self):
        return self.clean_pdf('process_3_pdf')

    def clean_process_4_pdf(self):
        return self.clean_pdf('process_4_pdf')
    
    def clean_pdf(self, field_name):
        pdf = self.cleaned_data.get(field_name)
        if pdf:
            if not pdf.name.lower().endswith('.pdf'):
                raise ValidationError("Only PDF files are allowed.")
            if pdf.size > 10 * 1024 * 1024:  # 10 MB limit
                raise ValidationError("File size cannot exceed 10 MB.")
        return pdf