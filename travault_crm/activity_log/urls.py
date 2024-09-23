# activity_log/urls.py

from django.urls import path
from . import views

app_name = 'activity_log'

urlpatterns = [
    path('company/<int:pk>/log-meeting/', views.log_meeting, name='log_meeting'),
    path('search-attendees/', views.search_attendees, name='search_attendees'),
    path('meeting/<int:pk>/', views.view_meeting, name='view_meeting'),
    path('meeting/<int:pk>/delete/', views.delete_meeting, name='delete_meeting'),
]