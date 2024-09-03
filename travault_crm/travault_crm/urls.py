# travault_crm/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('agencies/', include(('agencies.urls', 'agencies'), namespace='agencies')), 
    path('accounts/', include('allauth.urls')),
    path('dashboard/', include('dashboard.urls')),
]