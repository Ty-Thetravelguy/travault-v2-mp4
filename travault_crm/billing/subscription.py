# billing/subscription.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import stripe
from agencies.models import CustomUser
from .models import StripeCustomer

stripe.api_key = settings.STRIPE_SECRET_KEY

def update_subscription_quantity(stripe_customer):
    """Update the subscription quantity based on the number of users."""
    user_count = stripe_customer.agency.users.count()

    # Log for debugging
    print(f"Updating subscription: {stripe_customer.stripe_subscription_id} with user count: {user_count}")

    # Ensure subscription ID exists before modifying
    if not stripe_customer.stripe_subscription_id:
        raise ValueError("Stripe subscription ID is missing.")

    # Modify the subscription in Stripe
    stripe.Subscription.modify(
        stripe_customer.stripe_subscription_id,
        items=[{
            'price': settings.STRIPE_PRICE_ID,
            'quantity': user_count
        }]
    )

@receiver(post_save, sender=CustomUser)
def update_subscription_on_user_change(sender, instance, created, **kwargs):
    """Signal to update subscription when a user is added or updated."""
    if not instance.agency:
        print("User is not associated with an agency.")
        return

    try:
        # Check if the agency has a StripeCustomer
        stripe_customer = instance.agency.stripecustomer

        # Ensure subscription ID exists
        if not stripe_customer.stripe_subscription_id:
            print("Stripe subscription ID is missing for this agency.")
            return

        # Update the subscription quantity
        update_subscription_quantity(stripe_customer)

    except StripeCustomer.DoesNotExist:
        print("StripeCustomer record does not exist for this agency.")
    except Exception as e:
        print(f"Error updating subscription: {e}")
