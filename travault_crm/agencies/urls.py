# agencies/urls.py

from django.urls import path
from . import views  # Importing the whole views module

urlpatterns = [
    path('register/', views.AgencyRegistrationView.as_view(), name='agency_register'),
    path('login/', views.CustomLoginView.as_view(), name='account_login'),
    path('logout/', views.CustomLogoutView.as_view(), name='account_logout'),
    path('password/reset/', views.CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('password/reset/done/', views.CustomPasswordResetDoneView.as_view(), name='account_reset_password_done'),
    path('password/reset/key/<uidb36>/<key>/', views.CustomPasswordResetFromKeyView.as_view(), name='account_reset_password_from_key'),
    path('password/reset/key/done/', views.CustomPasswordResetFromKeyDoneView.as_view(), name='account_reset_password_from_key_done'),
    path('manage_users/', views.manage_users, name='manage_users'),  # Correctly reference manage_users via views
]