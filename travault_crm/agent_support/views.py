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
    print(f"Agency type: {type(request.user.agency)}")  # Debug line
    agency = request.user.agency

    # Check if agency is actually an Agency instance
    if not isinstance(agency, Agency):
        raise ValueError(f"Expected Agency instance, got {type(agency)}")

    suppliers = AgentSupportSupplier.objects.filter(agency=agency)
    return render(request, 'agent_support/index.html', {'suppliers': suppliers})


@login_required
def add_agent_supplier(request):
    if request.method == 'POST':
        form = AgentSupportSupplierForm(request.POST, request.FILES)
        if form.is_valid():
            agent_supplier = form.save(commit=False)
            agent_supplier.agency = request.user.agency  # Access agency correctly
            agent_supplier.user = request.user
            agent_supplier.save()
            return redirect('agent_support:index')
    else:
        form = AgentSupportSupplierForm()
    return render(request, 'agent_support/add_agent_supplier.html', {'form': form})


@login_required
def add_agent_supplier(request):
    agency = request.user.agency
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
    agency = request.user.agency
    supplier = get_object_or_404(AgentSupportSupplier, pk=pk, agency=agency)
    if request.method == 'POST':
        form = AgentSupportSupplierForm(request.POST, request.FILES, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('agent_support:index')
    else:
        form = AgentSupportSupplierForm(instance=supplier)
    return render(request, 'agent_support/edit_supplier.html', {'form': form})