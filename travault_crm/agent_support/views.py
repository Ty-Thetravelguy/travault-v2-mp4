from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AgentSupportSupplierForm
from .models import AgentSupportSupplier

from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def agent_support(request):
    # Ensure the user is linked to an agency
    if not request.user.agency:
        messages.error(request, 'You are not associated with any agency.')
        return redirect('home')  

    # Fetch suppliers linked to the user's agency
    suppliers = AgentSupportSupplier.objects.filter(agency=request.user.agency).order_by('supplier_name')
    supplier_types = AgentSupportSupplier.SUPPLIER_TYPES

    return render(request, 'agent_support/index.html', {
        'suppliers': suppliers,
        'supplier_types': supplier_types,
    })

@login_required
def add_agent_supplier(request):
    if request.method == 'POST':
        form = AgentSupportSupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.user = request.user
            
            # Link the supplier to the user's agency
            if request.user.agency:
                supplier.agency = request.user.agency
                supplier.save()
                messages.success(request, 'Supplier added successfully.')
                return redirect('agent_support:agent_support')
            else:
                messages.error(request, 'You are not associated with any agency. Please contact support.')
                return redirect('agent_support:agent_support')

        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AgentSupportSupplierForm()

    return render(request, 'agent_support/add_agent_supplier.html', {'form': form})