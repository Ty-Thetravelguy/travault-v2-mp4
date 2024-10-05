from django.urls import path
from . import views

urlpatterns = [
    path('open/<int:company_id>/', views.open_ticket, name='open_ticket'),
]
