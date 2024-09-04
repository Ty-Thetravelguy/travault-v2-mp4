# agencies/urls.py
from django.urls import path
from .views import confirm_email_and_setup_password
from . import views

urlpatterns = [
    path('register/', views.AgencyRegistrationView.as_view(), name='agency_register'),
    path('login/', views.CustomLoginView.as_view(), name='account_login'), 
    path('logout/', views.CustomLogoutView.as_view(), name='account_logout'),
    path('profile/', views.profile_view, name='profile'), 
    path('agency/profile/', views.agency_profile_view, name='agency_profile'),
    path('password/reset/', views.CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('password/reset/done/', views.CustomPasswordResetDoneView.as_view(), name='account_reset_password_done'),
    path('password/reset/key/<uidb36>/<key>/', views.CustomPasswordResetFromKeyView.as_view(),name='account_reset_password_from_key'),
    path('password/reset/key/done/', views.CustomPasswordResetFromKeyDoneView.as_view(), name='account_reset_password_from_key_done'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('add_user/', views.add_user, name='add_user'),
    path('accounts/confirm-email/<uidb64>/<token>/', confirm_email_and_setup_password, name='confirm_email_and_setup_password'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
]