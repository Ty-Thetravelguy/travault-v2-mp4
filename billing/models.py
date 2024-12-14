# billing/models.py

from django.db import models
from agencies.models import Agency

class StripeCustomer(models.Model):
    """
    Model representing a Stripe customer associated with an agency.

    Attributes:
        agency (OneToOneField): The agency associated with this Stripe customer.
        stripe_customer_id (str): The unique identifier for the Stripe customer.
        stripe_subscription_id (str): The unique identifier for the Stripe subscription.
        subscription_status (str): The current status of the subscription (e.g., active, inactive).
        created_at (DateTimeField): The timestamp when the customer was created.
        updated_at (DateTimeField): The timestamp when the customer was last updated.
    """
    agency = models.OneToOneField(Agency, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    subscription_status = models.CharField(max_length=50, default='inactive')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stripe customer for {self.agency.agency_name} - {self.subscription_status}"

class BillingInvoice(models.Model):
    """
    Model representing a billing invoice for an agency.

    Attributes:
        agency (ForeignKey): The agency associated with this invoice.
        stripe_invoice_id (str): The unique identifier for the Stripe invoice.
        amount (DecimalField): The total amount of the invoice.
        status (str): The current status of the invoice (e.g., paid, unpaid).
        invoice_pdf (URLField): A URL to the PDF of the invoice.
        created_at (DateTimeField): The timestamp when the invoice was created.
        paid_at (DateTimeField): The timestamp when the invoice was paid, if applicable.
    """
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