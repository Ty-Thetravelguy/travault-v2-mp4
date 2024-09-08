#agent_support/vies.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import AgentSupportSupplierForm
from .models import AgentSupportSupplier, Agency

from django.contrib.auth.decorators import login_required
# Create your views here.

CustomUser = get_user_model()

@login_required
def agent_support(request):
    # Check if user is an admin
    if request.user.user_type == 'admin':
        # Handle admin logic here, e.g., access all suppliers or bypass agency check
        suppliers = AgentSupportSupplier.objects.all().order_by('supplier_name')
    else:
        # Standard check for agency
        agency = request.user.agency
        if agency is None:
            return render(request, 'error.html', {'message': 'You are not associated with any agency. Please contact support.'})

       # suppliers = AgentSupportSupplier.objects.filter(agency=agency).order_by('supplier_name')
        suppliers = AgentSupportSupplier.objects.all().only('id', 'supplier_name')
        
    return render(request, 'agent_support/index.html', {'suppliers': suppliers})


@login_required
def add_agent_supplier(request):
    agency = request.user.profile.agency
    if request.method == 'POST':
        form = AgentSupportSupplierForm(request.POST, request.FILES)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.agency = agency
            supplier.save()
            return redirect('agent_support:index')
    else:
        form = AgentSupportSupplierForm()
    return render(request, 'agent_support/add_supplier.html', {'form': form})


@login_required
def edit_agent_supplier(request, pk):
    agency = request.user.profile.agency
    supplier = get_object_or_404(AgentSupportSupplier, pk=pk, agency=agency)
    if request.method == 'POST':
        form = AgentSupportSupplierForm(request.POST, request.FILES, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('agent_support:index')
    else:
        form = AgentSupportSupplierForm(instance=supplier)
    return render(request, 'agent_support/edit_supplier.html', {'form': form})