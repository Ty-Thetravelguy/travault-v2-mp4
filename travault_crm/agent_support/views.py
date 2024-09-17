import logging, time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import AgentSupportSupplier
from .forms import AgentSupportSupplierForm

# Initialize the logger
logger = logging.getLogger(__name__)

@login_required
def agent_support(request):
    """
    View to display agent support suppliers for the current user's agency.

    This view fetches and displays a list of agent support suppliers associated
    with the current user's agency. It ensures that suppliers are filtered correctly
    by the agency linked to the logged-in user.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.

    Returns:
        HttpResponse: Renders the agent_support/index.html template with a list of suppliers.
    """
    logger.info("Entering agent_support view.")
    start_time = time.time()

    # Fetch the current user's agency and filter suppliers accordingly
    agency = request.user.agency
    suppliers = AgentSupportSupplier.objects.filter(agency=agency).select_related('agency')
    logger.debug(f"Fetched {suppliers.count()} suppliers for agency '{agency.name}'.")

    logger.info(f"agent_support completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'agent_support/index.html', {'suppliers': suppliers})


@login_required
def add_agent_supplier(request):
    """
    View to add a new agent support supplier for the current user's agency.

    This view allows users to add a new agent support supplier by submitting a form.
    It handles both GET requests for displaying the blank form and POST requests for
    saving the new supplier.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.

    Returns:
        HttpResponse: Renders the add_agent_supplier template with the form,
        or redirects to the agent support view on successful addition.
    """
    logger.info("Entering add_agent_supplier view.")
    start_time = time.time()

    # Fetch the current user's agency
    agency = request.user.agency

    # Handle form submission for adding a new supplier
    if request.method == 'POST':
        form = AgentSupportSupplierForm(request.POST, request.FILES)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.agency = agency
            supplier.save()
            logger.info(f"New agent supplier '{supplier.name}' added for agency '{agency.name}'.")
            messages.success(request, "Agent supplier added successfully.")
            return redirect('agent_support:agent_support')
        else:
            logger.error(f"Form validation errors: {form.errors}.")
            messages.error(request, "Please correct the errors below.")

    # Initialize the form for GET requests
    else:
        form = AgentSupportSupplierForm()
        logger.debug("Initialized form for adding a new agent supplier.")

    logger.info(f"add_agent_supplier completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'agent_support/add_agent_supplier.html', {'form': form})


@login_required
def edit_agent_supplier(request, pk):
    """
    View to edit an existing agent support supplier.

    This view allows users to update an existing agent support supplier by submitting
    a form. It handles both GET requests for displaying the form with current supplier
    data, and POST requests for updating the supplier.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the supplier to be edited.

    Returns:
        HttpResponse: Renders the edit_agent_supplier template with the form and supplier details,
        or redirects to the agent support view on successful update.
    """
    logger.info(f"Entering edit_agent_supplier view for supplier pk={pk}.")
    start_time = time.time()

    # Fetch the current user's agency and the supplier to be edited
    agency = request.user.agency
    supplier = get_object_or_404(AgentSupportSupplier, pk=pk, agency=agency)
    logger.debug(f"Fetched supplier '{supplier.name}' for editing in agency '{agency.name}'.")

    # Handle form submission for updating the supplier
    if request.method == 'POST':
        form = AgentSupportSupplierForm(request.POST, request.FILES, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            logger.info(f"Agent supplier '{supplier.name}' updated successfully.")
            messages.success(request, "Agent supplier updated successfully.")
            return redirect('agent_support:agent_support')
        else:
            logger.error(f"Form validation errors: {form.errors}.")
            messages.error(request, "Please correct the errors below.")

    # Initialize the form with the current supplier instance for GET requests
    else:
        form = AgentSupportSupplierForm(instance=supplier)
        logger.debug("Initialized form for editing agent supplier.")

    logger.info(f"edit_agent_supplier completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'agent_support/edit_agent_supplier.html', {'form': form, 'supplier': supplier})
