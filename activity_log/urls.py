# activity_log/urls.py

from django.urls import path
from . import views

app_name = 'activity_log'

urlpatterns = [
    path('company/<int:pk>/log-meeting/', views.log_meeting, name='log_meeting'),
    path('company/<int:pk>/log-call/', views.log_call, name='log_call'),
    path('company/<int:pk>/log-email/', views.log_email, name='log_email'),
    path('search-attendees/', views.search_attendees, name='search_attendees'),
    path('meeting/<int:pk>/', views.view_meeting, name='view_meeting'),
    path('call/<int:pk>/', views.view_call, name='view_call'),
    path('email/<int:pk>/', views.view_email, name='view_email'),
    path('meeting/<int:pk>/delete/', views.delete_meeting, name='delete_meeting'),
    path('call/<int:pk>/delete/', views.delete_call, name='delete_call'),
    path('email/<int:pk>/delete/', views.delete_email, name='delete_email'),
]