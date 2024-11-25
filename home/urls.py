# home/urls.py

from django.urls import path
from .views import HomePageView, TermsOfServiceView, PrivacyPolicyView  # Add these imports

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('terms-of-service/', TermsOfServiceView.as_view(), name='terms_of_service'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
]