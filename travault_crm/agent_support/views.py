from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def agent_support(request):
    return render(request, 'agent_support/index.html')