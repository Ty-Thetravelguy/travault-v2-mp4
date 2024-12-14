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

    first_name = models.CharField(max_length=30, blank=True) 
    last_name = models.CharField(max_length=150, blank=True)  

    def get_full_name(self):
        """Return the first and last name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    def __str__(self):
        return self.get_full_name()


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

    agency_name = models.CharField("Agency Name", max_length=255)
    address = models.CharField("Business Address", max_length=255)
    phone = models.CharField("Phone Number", max_length=20)
    email = models.EmailField("Email Address")
    website = models.URLField("Website", blank=True, null=True)
    vat_number = models.CharField("VAT Number", max_length=9, unique=True)
    company_reg_number = models.CharField("Company Registration Number", max_length=8, unique=True)
    employees = models.CharField("Number of Employees", max_length=10, choices=EMPLOYEE_CHOICES)
    business_focus = models.CharField("Business Focus", max_length=20, choices=BUSINESS_FOCUS_CHOICES)
    contact_name = models.CharField("Primary Contact Name", max_length=100)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    updated_at = models.DateTimeField("Updated At", auto_now=True)

    @staticmethod
    def get_default_agency():
        return Agency.objects.first()

    def __str__(self):
        """
        String representation of the Agency object.

        Returns:
            str: The name of the agency.
        """
        return self.agency_name
