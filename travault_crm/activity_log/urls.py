# activity_log/urls.py

from django.urls import path
from . import views

app_name = 'activity_log'

urlpatterns = [
    path('company/<int:pk>/log-meeting/', views.log_meeting, name='log_meeting'),
    path('meeting/<int:pk>/', views.view_meeting, name='view_meeting'),
    # Other URL patterns will go here
]