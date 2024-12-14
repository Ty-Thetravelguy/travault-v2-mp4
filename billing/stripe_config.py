# billing/stripe_config.py

import stripe
from django.conf import settings

# Set the Stripe API key from the Django settings
stripe.api_key = settings.STRIPE_SECRET_KEY