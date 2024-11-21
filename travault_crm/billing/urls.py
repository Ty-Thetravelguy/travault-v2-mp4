# billing/urls.py
from django.urls import path
from . import views, webhooks 

app_name = 'billing'

urlpatterns = [
    path('setup-payment/', views.setup_payment, name='setup_payment'),
    path('portal/', views.billing_portal, name='billing_portal'),
    path('create-setup-intent/', views.create_setup_intent, name='create_setup_intent'),
    path('webhook/', webhooks.stripe_webhook, name='stripe_webhook'),
    path('error/', views.billing_error, name='billing_error'),
    path('subscription-inactive/', views.subscription_inactive, name='subscription_inactive'),
]