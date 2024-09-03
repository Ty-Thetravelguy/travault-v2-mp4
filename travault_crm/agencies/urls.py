# agencies/urls.py

from django.urls import path
from .views import AgencyRegistrationView
from agencies.views import CustomLoginView, CustomLogoutView, CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetFromKeyView, CustomPasswordResetFromKeyDoneView  # Add these imports

urlpatterns = [
    path('register/', AgencyRegistrationView.as_view(), name='agency_register'),
    path('login/', CustomLoginView.as_view(), name='account_login'),
    path('logout/', CustomLogoutView.as_view(), name='account_logout'),
    path('password/reset/', CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('password/reset/done/', CustomPasswordResetDoneView.as_view(), name='account_reset_password_done'),
    path('password/reset/key/<uidb36>/<key>/', CustomPasswordResetFromKeyView.as_view(), name='account_reset_password_from_key'),
    path('password/reset/key/done/', CustomPasswordResetFromKeyDoneView.as_view(), name='account_reset_password_from_key_done'),
]