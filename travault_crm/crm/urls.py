# crm/urls.py

from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.crm_index, name='index'),
    path('add_company/', views.add_company, name='add_company'),
    path('fetch-company-data/', views.fetch_company_data, name='fetch_company_data'),
    path('search-companies/', views.search_companies, name='search_companies'),
    path('company/<int:pk>/', views.company_detail, name='company_detail'),
    path('company/<int:pk>/edit/', views.edit_company, name='edit_company'),
    path('company/<int:pk>/delete/', views.delete_company, name='delete_company'),

]