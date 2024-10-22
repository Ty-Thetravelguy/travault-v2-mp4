# billing/urls.py
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('setup-payment/', views.setup_payment, name='setup_payment'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]