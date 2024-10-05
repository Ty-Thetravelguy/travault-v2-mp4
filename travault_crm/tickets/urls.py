from django.urls import path
from tickets import views
from . import views

app_name = 'tickets'

urlpatterns = [
    path('view/', views.view_tickets, name='view_tickets'),  # View tickets page
    path('open/<int:company_id>/', views.open_ticket, name='open_ticket'), 
    # path('category/create/', views.create_category, name='create_category'),  # Create a ticket category
]
