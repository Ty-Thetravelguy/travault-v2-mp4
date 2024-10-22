# billing/subscription.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import stripe
from agencies.models import CustomUser
from .models import StripeCustomer

stripe.api_key = settings.STRIPE_SECRET_KEY

def update_subscription_quantity(stripe_customer):
    """Update the subscription quantity based on number of users"""
    user_count = stripe_customer.agency.users.count()
    stripe.Subscription.modify(
        stripe_customer.stripe_subscription_id,
        items=[{
            'price': settings.STRIPE_PRICE_ID,
            'quantity': user_count
        }]
    )

@receiver(post_save, sender=CustomUser)
def update_subscription_on_user_change(sender, instance, created, **kwargs):
    if instance.agency and hasattr(instance.agency, 'stripecustomer'):
        update_subscription_quantity(instance.agency.stripecustomer)