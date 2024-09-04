# agent_support/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.agent_support, name='agent_support'),
]