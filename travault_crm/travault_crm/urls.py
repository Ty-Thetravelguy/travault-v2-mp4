# travault_crm/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('agencies/', include(('agencies.urls', 'agencies'), namespace='agencies')),  # Correctly namespaced
    path('accounts/', include('allauth.urls')),  # Allauth URLs included
    path('dashboard/', include('dashboard.urls')),
]