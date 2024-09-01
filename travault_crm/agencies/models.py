# agencies/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('agent', 'Agent'),
        ('manager', 'Manager'),
        ('sales', 'Sales'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='agent')
    agency = models.ForeignKey('Agency', on_delete=models.CASCADE, related_name='users', null=True, blank=True)

class Agency(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    vat_number = models.CharField(max_length=9, unique=True)
    company_reg_number = models.CharField(max_length=8, unique=True)
    employees = models.CharField(max_length=10)
    business_focus = models.CharField(max_length=20)
    contact_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name