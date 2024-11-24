# billing/models.py

from django.db import models
from agencies.models import Agency

class StripeCustomer(models.Model):
    agency = models.OneToOneField(Agency, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    subscription_status = models.CharField(max_length=50, default='inactive')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stripe customer for {self.agency.agency_name} - {self.subscription_status}"

class BillingInvoice(models.Model):
    agency = models.ForeignKey('agencies.Agency', on_delete=models.CASCADE)
    stripe_invoice_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    invoice_pdf = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice {self.stripe_invoice_id} for {self.agency.agency_name}"