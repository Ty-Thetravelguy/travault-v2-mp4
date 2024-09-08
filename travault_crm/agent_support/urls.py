# agent_support/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.agent_support, name='agent_support'),
    path('add_agent_supplier/', views.add_agent_supplier, name='add_agent_supplier'),
    path('edit_agent_supplier/<int:pk>/', views.edit_agent_supplier, name='edit_agent_supplier'),
]