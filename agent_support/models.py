# agent_support/models.py

from django.db import models
from agencies.models import Agency 
from django.core.files.storage import default_storage

def upload_to_s3(instance, filename):
    """
    Defines the upload path for files in S3.

    Args:
        instance (AgentSupportSupplier): The instance of the model containing the file.
        filename (str): The original filename of the file being uploaded.

    Returns:
        str: The S3 path where the file will be stored.
    """
    return f'pdfs/{instance.supplier_type}/{filename}'

class AgentSupportSupplier(models.Model):
    """
    Model representing a supplier that provides support for agents.

    Attributes:
        agency (ForeignKey): The agency associated with this supplier.
        supplier_type (str): The type of supplier, chosen from SUPPLIER_TYPES.
        supplier_name (str): The name of the supplier.
        agent_websites (str): Websites associated with the supplier, can be blank.
        contact_numbers (str): Contact numbers for the supplier, can be blank.
        group_email (str): Group email for contacting the supplier, can be blank.
        general_email (str): General email for contacting the supplier, can be blank.
        account_manager (str): Name of the account manager, can be blank.
        account_manager_contact (str): Contact information for the account manager, can be blank.
        account_manager_email (EmailField): Email of the account manager, can be blank.
        other (str): Other miscellaneous information about the supplier, can be blank.
        process_1_subject (str): Subject for the first process, can be blank.
        process_1_text (str): Text description for the first process, can be blank.
        process_1_pdf (FileField): PDF file associated with the first process, can be blank.
        process_2_subject (str): Subject for the second process, can be blank.
        process_2_text (str): Text description for the second process, can be blank.
        process_2_pdf (FileField): PDF file associated with the second process, can be blank.
        process_3_subject (str): Subject for the third process, can be blank.
        process_3_text (str): Text description for the third process, can be blank.
        process_3_pdf (FileField): PDF file associated with the third process, can be blank.
        process_4_subject (str): Subject for the fourth process, can be blank.
        process_4_text (str): Text description for the fourth process, can be blank.
        process_4_pdf (FileField): PDF file associated with the fourth process, can be blank.
        file (FileField): An additional file associated with the supplier, can be blank.
        """

    SUPPLIER_TYPES = [
        ('air', 'Air'),
        ('accommodation', 'Accommodation'),
        ('ground_transportation', 'Ground Transportation'),
        ('rail', 'Rail'), 
        ('other', 'Other')
    ]
    
    # Links the supplier to an agency, with cascading delete if the agency is removed
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='agent_support_suppliers')

    supplier_type = models.CharField(max_length=50, choices=SUPPLIER_TYPES)  # Type of supplier
    supplier_name = models.CharField(max_length=100)  # Name of the supplier
    agent_websites = models.TextField(blank=True, null=True)  # Associated websites, optional
    contact_numbers = models.TextField(blank=True, null=True)  # Contact numbers, optional
    group_email = models.TextField(blank=True, null=True)  # Group email addresses, optional
    general_email = models.TextField(blank=True, null=True)  # General email addresses, optional
    account_manager = models.CharField(max_length=100, blank=True, null=True)  # Account manager's name, optional
    account_manager_contact = models.CharField(max_length=100, blank=True, null=True)  # Account manager's contact, optional
    account_manager_email = models.EmailField(blank=True, null=True)  # Account manager's email, optional
    other = models.TextField(blank=True, null=True)  # Other relevant information, optional
    
    # Process-related fields to handle different types of processes linked to the supplier
    process_1_subject = models.CharField(max_length=100, blank=True, null=True)
    process_1_text = models.TextField(blank=True, null=True)
    process_1_pdf = models.FileField(upload_to=upload_to_s3, blank=True, null=True)

    process_2_subject = models.CharField(max_length=100, blank=True, null=True)
    process_2_text = models.TextField(blank=True, null=True)
    process_2_pdf = models.FileField(upload_to=upload_to_s3, blank=True, null=True)

    process_3_subject = models.CharField(max_length=100, blank=True, null=True)
    process_3_text = models.TextField(blank=True, null=True)
    process_3_pdf = models.FileField(upload_to=upload_to_s3, blank=True, null=True)

    process_4_subject = models.CharField(max_length=100, blank=True, null=True)
    process_4_text = models.TextField(blank=True, null=True)
    process_4_pdf = models.FileField(upload_to=upload_to_s3, blank=True, null=True)

    # A general file associated with the supplier, stored in S3
    file = models.FileField(upload_to=upload_to_s3, blank=True, null=True)

    def __str__(self):
        """
        String representation of the AgentSupportSupplier object.

        Returns:
            str: A string combining the supplier name and the display version of the supplier type.
        """
        return f"{self.supplier_name} - {self.get_supplier_type_display()}"
