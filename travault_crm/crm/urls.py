# crm/urls.py

from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.crm_index, name='index'),
    path('company/<int:company_id>/', views.company_detail, name='company_detail'), 
    path('add_company/', views.add_company, name='add_company'),
    path('fetch-company-data/', views.fetch_company_data, name='fetch_company_data'),
    path('search-companies/', views.search_companies, name='search_companies'),
]