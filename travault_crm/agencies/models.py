# agencies/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.

    Attributes:
        user_type (str): The type of user, selected from USER_TYPE_CHOICES. Defaults to 'admin'.
        agency (ForeignKey): A foreign key linking the user to an Agency. Can be null or blank.
        first_name (str): The first name of the user. Allows blank values.
        last_name (str): The last name of the user. Allows blank values.
    """

    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('agent', 'Agent'),
        ('manager', 'Manager'),
        ('sales', 'Sales'),
    )

    # Defines the type of user, which determines their permissions and role in the system
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='admin')

    # Links the user to an Agency; allows multiple users to be associated with a single agency
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE, related_name='users', null=True, blank=True)

    first_name = models.CharField(max_length=30, blank=True)  # Optional first name
    last_name = models.CharField(max_length=150, blank=True)  # Optional last name


class Agency(models.Model):
    """
    Model representing an agency.

    Attributes:
        agency_name (str): The name of the agency.
        address (str): The full address of the agency.
        phone (str): The contact phone number of the agency.
        email (str): The contact email address of the agency.
        website (URL): The website URL of the agency, optional.
        vat_number (str): The VAT number of the agency, must be unique.
        company_reg_number (str): The company registration number, must be unique.
        employees (str): The size of the agency in terms of employees, chosen from EMPLOYEE_CHOICES.
        business_focus (str): The main business focus of the agency, chosen from BUSINESS_FOCUS_CHOICES.
        contact_name (str): The primary contact person's name for the agency.
        created_at (DateTime): Timestamp when the agency record was created.
        updated_at (DateTime): Timestamp when the agency record was last updated.
    """

    # Choices for the number of employees in the agency
    EMPLOYEE_CHOICES = [
        ('1-10', '1-10'),
        ('11-50', '11-50'),
        ('51-100', '51-100'),
        ('100+', '100+'),
    ]

    # Choices for the business focus of the agency
    BUSINESS_FOCUS_CHOICES = [
        ('corporate', 'Corporate Travel'),
        ('leisure', 'Leisure Travel'),
        ('mixed', 'Mixed'),
    ]

    agency_name = models.CharField(max_length=255)  # Name of the agency
    address = models.TextField()  # Physical address of the agency
    phone = models.CharField(max_length=20)  # Contact phone number for the agency
    email = models.EmailField()  # Contact email for the agency
    website = models.URLField(blank=True, null=True)  # Optional website URL for the agency
    vat_number = models.CharField(max_length=9, unique=True)  # Unique VAT number of the agency
    company_reg_number = models.CharField(max_length=8, unique=True)  # Unique company registration number
    employees = models.CharField(max_length=10, choices=EMPLOYEE_CHOICES)  # Size of the agency
    business_focus = models.CharField(max_length=20, choices=BUSINESS_FOCUS_CHOICES)  # Business focus of the agency
    contact_name = models.CharField(max_length=100)  # Primary contact person for the agency
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set date/time when the record is created
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated date/time when the record is updated

    def __str__(self):
        """
        String representation of the Agency object.

        Returns:
            str: The name of the agency.
        """
        return self.agency_name
