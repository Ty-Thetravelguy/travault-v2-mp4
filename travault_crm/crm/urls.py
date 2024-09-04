# crm/urls.py

from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.crm_index, name='index'),
    path('company/<int:company_id>/', views.company_detail, name='company_detail'), 
]