# crm/urls.py

from django.urls import path
from . import views
from activity_log import views as activity_views

app_name = 'crm'

urlpatterns = [
    path('', views.crm_index, name='index'),
    path('add_company/', views.add_company, name='add_company'),  
    path('company/<int:pk>/edit/', views.edit_company, name='edit_company'),
    path('company/<int:pk>/delete/', views.delete_company, name='delete_company'),
    path('company/<int:pk>/add-contact/', views.add_contact, name='add_contact'), 
    path('company/<int:pk>/edit-notes/', views.edit_company_notes, name='edit_company_notes'),
    path('company/<int:pk>/add-notes/', views.add_company_notes, name='add_company_notes'),
    path('company/<int:company_pk>/activity-log/', activity_views.activity_log, name='activity_log'),
    path('fetch-company-data/', views.fetch_company_data, name='fetch_company_data'),
    path('search-companies/', views.search_companies, name='search_companies'),
    path('company/<int:pk>/add-transaction-fee/', views.add_transaction_fee, name='add_transaction_fee'),
    path('company/<int:pk>/', views.company_detail, name='company_detail'),
    path('company/<int:pk>/<str:active_tab>/', views.company_detail, name='company_detail_with_tab'),

    path('contact/<int:pk>/', views.contact_detail, name='contact_detail'),
    path('contact/<int:pk>/edit/', views.edit_contact, name='edit_contact'),
    path('contact/<int:pk>/delete/', views.delete_contact_view, name='delete_contact_view'),
    path('contact/<int:pk>/delete/confirm/', views.confirm_delete_contact, name='confirm_delete_contact'),
    
    
    path('transaction-fee/<int:pk>/edit/', views.edit_transaction_fee, name='edit_transaction_fee'),
    path('transaction-fee/<int:pk>/delete/', views.delete_transaction_fee, name='delete_transaction_fee'),
    path('company/<int:pk>/log-call/', activity_views.log_call, name='log_call'),
    path('company/<int:pk>/log-email/', activity_views.log_email, name='log_email'),
    path('company/<int:pk>/log-meeting/', activity_views.log_meeting, name='log_meeting'),
    path('company/<int:pk>/open-ticket/', activity_views.open_ticket, name='open_ticket'),
    path('company/<int:pk>/start-deal/', activity_views.start_deal, name='start_deal'),
]