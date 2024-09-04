from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def agent_support(request):
    return render(request, 'agent_support/index.html')

@login_required
def add_agent_supplier(request):
    return render(request, 'agent_support/add_agent_supplier.html')