# billing/urls.py
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('setup-payment/', views.setup_payment, name='setup_payment'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('error/', views.billing_error, name='billing_error'),  # Add this line
    path('billing-portal/', views.billing_portal, name='billing_portal'),
    path('subscription-inactive/', views.subscription_inactive, name='subscription_inactive'),
]