# agencies/models.py

from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('agent', 'Agent'),
        ('manager', 'Manager'),
        ('sales', 'Sales'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='admin')
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

class Agency(models.Model):
    EMPLOYEE_CHOICES = [
        ('1-10', '1-10'),
        ('11-50', '11-50'),
        ('51-100', '51-100'),
        ('100+', '100+'),
    ]

    BUSINESS_FOCUS_CHOICES = [
        ('corporate', 'Corporate Travel'),
        ('leisure', 'Leisure Travel'),
        ('mixed', 'Mixed'),
    ]

    agency_name = models.CharField(max_length=255)  # Updated field name
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    vat_number = models.CharField(max_length=9, unique=True)
    company_reg_number = models.CharField(max_length=8, unique=True)
    employees = models.CharField(max_length=10, choices=EMPLOYEE_CHOICES)
    business_focus = models.CharField(max_length=20, choices=BUSINESS_FOCUS_CHOICES)
    contact_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.agency_name
