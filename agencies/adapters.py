# activity_log/adapters.py

from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect
from django.contrib import messages
from billing.models import StripeCustomer

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter to enforce payment setup before allowing login.
    This adapter checks if the user has a valid Stripe subscription
    associated with their agency before proceeding with the login process.
    """
    def login(self, request, user):
        """
        Overrides the login method to enforce payment setup.
        If the user's agency does not have a valid Stripe subscription,
        an error message is displayed and the user is redirected to the payment setup page.
        """
        # Check if the user's agency has a valid Stripe subscription
        try:
            stripe_customer = user.agency.stripecustomer
            if not stripe_customer.stripe_subscription_id:
                messages.error(request, "You must complete payment setup before logging in.")
                return redirect('billing:setup_payment')
        except StripeCustomer.DoesNotExist:
            messages.error(request, "You must complete payment setup before logging in.")
            return redirect('billing:setup_payment')

        # Proceed with login if payment setup is complete
        super().login(request, user)