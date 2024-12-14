# billing/admin.py

from django.contrib import admin
from .models import StripeCustomer, BillingInvoice

@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    """
    Admin interface for managing StripeCustomer instances.

    This class customizes the admin interface for the StripeCustomer model,
    allowing for easy management of customer data.

    Attributes:
        list_display (tuple): Fields to display in the list view.
        list_filter (tuple): Fields to filter the list view.
        search_fields (tuple): Fields to search within the list view.
        readonly_fields (tuple): Fields that are read-only in the admin interface.
        ordering (tuple): Default ordering of the list view.
    """
    list_display = ('agency', 'stripe_customer_id', 'stripe_subscription_id', 'subscription_status', 'created_at')
    list_filter = ('subscription_status',)
    search_fields = ('agency__agency_name', 'stripe_customer_id', 'stripe_subscription_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(BillingInvoice)
class BillingInvoiceAdmin(admin.ModelAdmin):
    """
    Admin interface for managing BillingInvoice instances.

    This class customizes the admin interface for the BillingInvoice model,
    allowing for easy management of invoice data.

    Attributes:
        list_display (tuple): Fields to display in the list view.
        list_filter (tuple): Fields to filter the list view.
        search_fields (tuple): Fields to search within the list view.
        readonly_fields (tuple): Fields that are read-only in the admin interface.
        ordering (tuple): Default ordering of the list view.
    """
    list_display = ('agency', 'stripe_invoice_id', 'amount', 'status', 'created_at', 'paid_at')
    list_filter = ('status',)
    search_fields = ('agency__agency_name', 'stripe_invoice_id')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)