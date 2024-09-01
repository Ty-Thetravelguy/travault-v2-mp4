from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard_view(request):
    # Your dashboard logic here
    return render(request, 'dashboard/dashboard.html')