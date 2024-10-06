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
    # path('category/create/', views.create_category, name='create_category'),  # Create a ticket category
]
