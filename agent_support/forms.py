# agent_support/forms.py

from django import forms
from .models import AgentSupportSupplier
from django.core.exceptions import ValidationError

class AgentSupportSupplierForm(forms.ModelForm):
    """
    Form for creating and updating AgentSupportSupplier instances.

    Includes fields for supplier details, contact information, and multiple
    process-specific fields that can include subject text, description text, and PDFs.

    Fields:
        - supplier_type: The type of the supplier (e.g., Air, Accommodation).
        - supplier_name: The name of the supplier.
        - agent_websites: Websites associated with the supplier, entered as comma-separated values.
        - contact_numbers: Contact numbers for the supplier, entered as comma-separated values.
        - group_email: Group email addresses for the supplier, entered as comma-separated values.
        - general_email: General email addresses for the supplier, entered as comma-separated values.
        - account_manager: Name of the account manager for the supplier.
        - account_manager_contact: Contact information for the account manager.
        - account_manager_email: Email address of the account manager.
        - other: Miscellaneous additional information about the supplier.
        - process_X_subject: Subject for process X, where X ranges from 1 to 4.
        - process_X_text: Text description for process X.
        - process_X_pdf: PDF file associated with process X.
    """

    # Text fields for websites, contact numbers, and emails with specific formatting instructions
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

    # Fields for the process subjects, descriptions, and PDF uploads
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
        """
        Meta class for AgentSupportSupplierForm.

        Specifies the model and fields used in the form, as well as ordering the fields.
        """
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

    def clean_pdf(self, field_name):
        """
        Validates the uploaded PDF file for a specific field.

        Ensures that the uploaded file is a PDF and that it does not exceed 10 MB in size.

        Args:
            field_name (str): The name of the file field to clean.

        Raises:
            ValidationError: If the file is not a PDF or exceeds the size limit.

        Returns:
            file: The cleaned file data for the specified field.
        """
        pdf = self.cleaned_data.get(field_name)
        if pdf:
            if not pdf.name.lower().endswith('.pdf'):
                raise ValidationError("Only PDF files are allowed.")
            if pdf.size > 10 * 1024 * 1024:  # 10 MB limit
                raise ValidationError("File size cannot exceed 10 MB.")
        return pdf

    # Specific clean methods for each process PDF field, calling the generic clean_pdf method
    def clean_process_1_pdf(self):
        return self.clean_pdf('process_1_pdf')

    def clean_process_2_pdf(self):
        return self.clean_pdf('process_2_pdf')

    def clean_process_3_pdf(self):
        return self.clean_pdf('process_3_pdf')

    def clean_process_4_pdf(self):
        return self.clean_pdf('process_4_pdf')