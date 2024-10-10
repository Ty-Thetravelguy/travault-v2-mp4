from django.urls import path
from tickets import views
from . import views

app_name = 'tickets'

urlpatterns = [
    path('open/<int:company_id>/', views.open_ticket, name='open_ticket'), 
    path('detail/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('detail/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('ticket-subject-autocomplete/', views.ticket_subject_autocomplete, name='ticket-subject-autocomplete'),
    path('create-ticket-subject/', views.create_ticket_subject, name='create-ticket-subject'),
    path('view/', views.view_tickets, name='view_tickets'),  # View tickets page
    path('<int:pk>/update-field/', views.update_ticket_field, name='update_ticket_field'),
    path('<int:pk>/edit/', views.edit_ticket, name='edit_ticket'),
    path('delete/<int:pk>/confirm/', views.delete_ticket_confirm, name='delete_ticket_confirm'),
    path('preview-email/<int:ticket_id>/', views.preview_ticket_email, name='preview_ticket_email'),
    path('manage-subjects/', views.manage_subjects, name='manage_subjects'),
    path('update-subject/<int:subject_id>/', views.update_subject, name='update_subject'),
    path('delete-subject/<int:subject_id>/', views.delete_subject, name='delete_subject'),
    path('<int:pk>/add-action/', views.add_ticket_action, name='add_ticket_action'),
    path('action/<int:action_id>/edit/', views.edit_ticket_action, name='edit_ticket_action'),
    path('action/<int:action_id>/delete/', views.delete_ticket_action, name='delete_ticket_action'),
    path('view-email/<str:email_type>/<int:ticket_id>/', views.view_email_in_browser, name='view_email_in_browser'),
]
