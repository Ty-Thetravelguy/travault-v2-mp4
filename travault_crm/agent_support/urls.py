# agent_support/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.agent_support, name='agent_support'),
    path('add_agent_supplier/', views.add_agent_supplier, name='add_agent_supplier'),
]