# agent_support/views.py

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import AgentSupportSupplier
from .forms import AgentSupportSupplierForm
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


@login_required
def agent_support(request):
    # Ensure we're filtering by the correct Agency instance linked to the user
    agency = request.user.agency  # Assuming the CustomUser model includes agency
    suppliers = AgentSupportSupplier.objects.filter(agency=agency).select_related('agency')

    return render(request, 'agent_support/index.html', {'suppliers': suppliers})

@login_required
def add_agent_supplier(request):
    agency = request.user.agency

    if request.method == 'POST':
        form = AgentSupportSupplierForm(request.POST, request.FILES)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.agency = agency
            supplier.save()
            return redirect('agent_support:agent_support')
    else:
        form = AgentSupportSupplierForm()

    return render(request, 'agent_support/add_agent_supplier.html', {'form': form})

# @login_required
# def edit_agent_supplier(request, pk):
#     # Print the storage backend being used
#     print(default_storage.__class__.__name__)  # This should output 'S3Boto3Storage'

#     agency = request.user.agency
#     supplier = get_object_or_404(AgentSupportSupplier, pk=pk, agency=agency)

#     if request.method == 'POST':
#         form = AgentSupportSupplierForm(request.POST, request.FILES, instance=supplier)
#         if form.is_valid():
#             form.save()
#             return redirect('agent_support:agent_support')
#     else:
#         form = AgentSupportSupplierForm(instance=supplier)

#     return render(request, 'agent_support/edit_agent_supplier.html', {'form': form, 'supplier': supplier})

@login_required
def edit_agent_supplier(request, pk):
    logger.debug(f"Starting edit_agent_supplier view for pk: {pk}")
    logger.debug(f"Default storage: {default_storage.__class__.__name__}")

    agency = request.user.agency
    supplier = get_object_or_404(AgentSupportSupplier, pk=pk, agency=agency)

    if request.method == 'POST':
        logger.debug("Processing POST request")
        form = AgentSupportSupplierForm(request.POST, request.FILES, instance=supplier)
        if form.is_valid():
            logger.debug("Form is valid, processing file fields")
            for field_name in ['process_1_pdf', 'process_2_pdf', 'process_3_pdf', 'process_4_pdf']:
                if field_name in request.FILES:
                    file = request.FILES[field_name]
                    logger.debug(f"Processing {field_name}: {file.name}")
                    try:
                        path = default_storage.save(f'pdfs/{field_name}/{file.name}', file)
                        logger.debug(f"File saved to path: {path}")
                        setattr(supplier, field_name, path)
                    except Exception as e:
                        logger.error(f"Error saving {field_name}: {str(e)}")
            
            supplier = form.save()
            logger.debug(f"Supplier saved. PDF fields: {supplier.process_1_pdf}, {supplier.process_2_pdf}, {supplier.process_3_pdf}, {supplier.process_4_pdf}")
            return redirect('agent_support:agent_support')
        else:
            logger.debug(f"Form is invalid. Errors: {form.errors}")
    else:
        logger.debug("Processing GET request")
        form = AgentSupportSupplierForm(instance=supplier)

    logger.debug("Rendering edit_agent_supplier template")
    return render(request, 'agent_support/edit_agent_supplier.html', {'form': form, 'supplier': supplier})
