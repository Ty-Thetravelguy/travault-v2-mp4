from django.contrib import admin
from .models import StripeCustomer, BillingInvoice

@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    list_display = ('agency', 'stripe_customer_id', 'stripe_subscription_id', 'subscription_status', 'created_at')
    list_filter = ('subscription_status',)
    search_fields = ('agency__agency_name', 'stripe_customer_id', 'stripe_subscription_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(BillingInvoice)
class BillingInvoiceAdmin(admin.ModelAdmin):
    list_display = ('agency', 'stripe_invoice_id', 'amount', 'status', 'created_at', 'paid_at')
    list_filter = ('status',)
    search_fields = ('agency__agency_name', 'stripe_invoice_id')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)