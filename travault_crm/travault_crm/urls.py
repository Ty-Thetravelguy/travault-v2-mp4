# travault_crm/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('agencies/', include(('agencies.urls', 'agencies'), namespace='agencies')), 
    path('accounts/', include('allauth.urls')),  # Allauth URLs included
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),  
    path('agent_support/', include(('agent_support.urls', 'agent_support'), namespace='agent_support')),  
    path('crm/', include(('crm.urls', 'crm'), namespace='crm')),
]