# agencies/urls.py

from django.urls import path
from .views import AgencyRegistrationView

urlpatterns = [
    path('register/', AgencyRegistrationView.as_view(), name='agency_register'),  # Changed from 'registration/' to 'register/'
]