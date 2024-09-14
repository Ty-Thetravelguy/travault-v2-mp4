#crm/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.contrib import messages
import requests
from .models import Company, COMPANY_TYPE_CHOICES, Contact, CompanyNotes, TransactionFee
from .forms import CompanyForm, ContactForm, CompanyNotesForm, TransactionFeeForm
from urllib.parse import quote
from django.conf import settings
from django.db.models import Case, When, BooleanField
import logging
import time
from activity_log.models import ActivityLog 

logger = logging.getLogger(__name__)
User = get_user_model()


@login_required
def crm_index(request):
    """
    View for the CRM index page.
    
    This view displays a list of companies associated with the user's agency 
    and allows filtering and ordering of companies. It also provides a list 
    of company owners who are either admin or sales users.
    
    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        
    Returns:
        HttpResponse: Renders the CRM index template with a context containing
        companies, company type choices, and company owners.
    """
    
    # Log entry into the view
    logger.info("Entered crm_index view.")
    
    # Start time tracking for performance logging
    start_time = time.time()

    # Retrieve the user's agency to filter companies
    agency = request.user.agency
    logger.debug(f"Fetching companies for agency: {agency}")
    
    # Fetch companies associated with the user's agency, ordered by creation date
    try:
        companies = Company.objects.filter(agency=agency).order_by('-create_date')
        logger.debug(f"Fetched {companies.count()} companies for agency {agency}.")
    except Exception as e:
        logger.error(f"Error fetching companies for agency {agency}: {e}")
        companies = []  # Fallback in case of error to prevent view failure

    # Fetch users who can be company owners (admin or sales roles) within the agency
    try:
        company_owners = User.objects.filter(agency=agency, user_type__in=['admin', 'sales'])
        logger.debug(f"Fetched {company_owners.count()} company owners for agency {agency}.")
    except Exception as e:
        logger.error(f"Error fetching company owners for agency {agency}: {e}")
        company_owners = []  # Fallback in case of error

    # Prepare context for rendering the template
    context = {
        'companies': companies,
        'company_type_choices': COMPANY_TYPE_CHOICES,
        'company_owners': company_owners,
    }

    # Log the completion of the view with performance time
    logger.info(f"crm_index completed in {time.time() - start_time:.2f} seconds.")

    # Render the index page with the prepared context
    return render(request, 'crm/index.html', context)


@login_required
def company_detail(request, pk, active_tab='details'):
    """
    View for displaying the details of a specific company.

    This view fetches the details of a company based on the provided primary key (pk),
    along with related data such as contacts, notes, transaction fees, and activity logs.
    It allows navigation between different tabs to display company-specific information.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the company to be displayed.
        active_tab (str): The currently active tab in the UI. Defaults to 'details'.

    Returns:
        HttpResponse: Renders the company_detail template with a context containing
        the company details, related contacts, notes, transaction fees, activity logs, and forms.
    """
    
    # Log entry into the view
    logger.info(f"Entering company_detail view for company pk={pk}.")
    
    # Start time tracking for performance logging
    start_time = time.time()

    # Fetch the company based on pk and user's agency, with error handling
    try:
        company = get_object_or_404(Company, pk=pk, agency=request.user.agency)
        logger.debug(f"Company fetched: {company.company_name}.")
    except Exception as e:
        logger.error(f"Error fetching company with pk={pk}: {e}")
        raise  # Reraise the exception after logging

    # Fetch all companies associated with the user's agency
    try:
        companies = Company.objects.filter(agency=request.user.agency)
        logger.debug(f"Fetched {companies.count()} companies for agency {request.user.agency}.")
    except Exception as e:
        logger.error(f"Error fetching companies for agency {request.user.agency}: {e}")
        companies = []  # Fallback to an empty list to avoid breaking the view

    # Fetch company notes, handling the case where notes might not exist
    try:
        company_notes = company.notes
        logger.debug("Company notes fetched successfully.")
    except CompanyNotes.DoesNotExist:
        company_notes = None
        logger.warning(f"No company notes found for company pk={pk}.")

    # Fetch transaction fees associated with the company
    transaction_fees = company.transaction_fees.all()
    logger.debug(f"Fetched {transaction_fees.count()} transaction fees for company pk={pk}.")

    # Initialize the form for adding new transaction fees and forms for editing existing fees
    fee_form = TransactionFeeForm()
    edit_forms = {fee.id: TransactionFeeForm(instance=fee) for fee in transaction_fees}
    logger.debug(f"Prepared forms for adding and editing transaction fees for company pk={pk}.")

    # Fetch and annotate contacts related to the company, sorting primary contacts first
    contacts = company.contacts.annotate(
        is_primary=Case(
            When(is_primary_contact=True, then=True),
            default=False,
            output_field=BooleanField(),
        )
    ).order_by('-is_primary', 'first_name', 'last_name')
    logger.debug(f"Fetched and sorted {contacts.count()} contacts for company pk={pk}.")

    # Filter contacts into specific categories
    travel_bookers = contacts.filter(is_travel_booker_contact=True)
    vip_travellers = contacts.filter(is_vip_traveller_contact=True)
    logger.debug(f"Filtered {travel_bookers.count()} travel bookers and {vip_travellers.count()} VIP travellers.")

    # Activity Log
    activities = ActivityLog.objects.filter(company=company)

    # Prepare the context for rendering the template
    context = {
        'company': company,
        'companies': companies,
        'contacts': contacts,
        'travel_bookers': travel_bookers,
        'vip_travellers': vip_travellers,
        'company_notes': company_notes,
        'transaction_fees': transaction_fees,
        'fee_form': fee_form,
        'edit_forms': edit_forms,
        'activities': activities,
        'active_tab': active_tab or 'details',
    }

    # Log the completion of the view with performance time
    logger.info(f"company_detail completed in {time.time() - start_time:.2f} seconds.")

    # Render the company detail page with the prepared context
    return render(request, 'crm/company_detail.html', context)


@login_required
def edit_company(request, pk):
    """
    View to edit the details of a specific company.

    This view allows users to update the details of a company by submitting a form.
    It handles both GET requests for displaying the form with current company data,
    and POST requests for updating the data.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the company to be edited.

    Returns:
        HttpResponse: Renders the edit_company template with the form and company details,
        or redirects to the company detail view on successful update.
    """
    logger.info(f"Entering edit_company view for company pk={pk}.")
    start_time = time.time()

    # Fetch the company based on pk and user's agency
    company = get_object_or_404(Company, pk=pk, agency=request.user.agency)
    logger.debug(f"Fetched company: {company.company_name} for editing.")

    # Handle form submission for updating company details
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company, agency=request.user.agency)
        if form.is_valid():
            company = form.save(commit=False)
            company.save()
            form.save_m2m()  # Save many-to-many relationships
            logger.info(f"Company '{company.company_name}' successfully updated.")
            messages.success(request, f"Company '{company.company_name}' has been successfully updated.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='details')
        else:
            logger.error(f"Form validation errors: {form.errors}")
    
    # Initialize the form with the current company instance for GET requests
    else:
        form = CompanyForm(instance=company, agency=request.user.agency)
        logger.debug("Initialized form for company editing.")

    # Prepare context and render the form
    context = {
        'form': form,
        'company': company,
    }

    logger.info(f"edit_company completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'crm/edit_company.html', context)


@login_required
def delete_company(request, pk):
    """
    View to delete a specific company.

    This view allows users to delete a company from the database. It shows a confirmation
    page and handles the deletion upon POST request.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the company to be deleted.

    Returns:
        HttpResponse: Redirects to the CRM index view on successful deletion,
        or renders a confirmation page.
    """
    logger.info(f"Entering delete_company view for company pk={pk}.")
    start_time = time.time()

    # Fetch the company based on pk and user's agency
    company = get_object_or_404(Company, pk=pk, agency=request.user.agency)
    logger.debug(f"Fetched company: {company.company_name} for deletion.")

    if request.method == 'POST':
        company.delete()
        logger.info(f"Company '{company.company_name}' successfully deleted.")
        messages.success(request, f"Company '{company.company_name}' has been successfully deleted.")
        return redirect('crm:index')

    # Render a confirmation page for GET requests
    logger.info(f"delete_company completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'crm/delete_company_confirm.html', {'company': company})


@login_required
def add_company(request):
    """
    View to add a new company.

    This view allows users to create a new company by submitting a form. It handles
    both GET requests for displaying the blank form and POST requests for saving the new company.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.

    Returns:
        HttpResponse: Renders the add_company template with the form, or redirects
        to the CRM index view on successful addition.
    """
    logger.info("Entering add_company view.")
    start_time = time.time()

    agency = request.user.agency

    # Handle form submission for adding a new company
    if request.method == 'POST':
        form = CompanyForm(request.POST, agency=agency)
        if form.is_valid():
            company = form.save(commit=False)
            company.agency = agency
            company.save()
            form.save_m2m()  # Save many-to-many relationships
            logger.info(f"Company '{company.company_name}' successfully added.")
            messages.success(request, f"Company '{company.company_name}' has been successfully added.")
            return redirect('crm:index')
        else:
            logger.error(f"Form validation errors: {form.errors}")

    # Initialize the form for GET requests
    else:
        form = CompanyForm(agency=agency)
        logger.debug("Initialized form for adding a new company.")

    # Prepare context and render the form
    logger.info(f"add_company completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'crm/add_company.html', {'form': form})


@login_required
def fetch_company_data(request):
    """
    View to fetch company data from an external API.

    This view takes a website URL as a query parameter, calls an external API to fetch
    company information, and returns the data as a JSON response.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.

    Returns:
        JsonResponse: Contains the fetched company data or an error message.
    """
    logger.info("Entering fetch_company_data view.")
    start_time = time.time()

    # Get the website URL from the request
    website = request.GET.get('website', '').strip()
    if not website:
        logger.error("Website parameter not provided.")
        return JsonResponse({'error': 'Website not provided'}, status=400)

    # Check for API key availability
    api_key = settings.DIFFBOT_API_KEY
    if not api_key:
        logger.error("Diffbot API key is missing in settings.")
        return JsonResponse({'error': 'API key is missing'}, status=500)

    # Prepare the API request
    encoded_website = quote(website)
    full_url = f'https://api.diffbot.com/v3/analyze?url={encoded_website}&token={api_key}&timeout=50000'

    try:
        # Call the external API
        response = requests.get(full_url, timeout=60)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()

        # Extract company data if available
        if 'objects' in data and data['objects']:
            company_obj = data['objects'][0]
            location = company_obj.get('locations', [{}])[0]

            phone_number = ''
            if company_obj.get('phoneNumbers'):
                phone_number = company_obj['phoneNumbers'][0].get('string', '')

            company_data = {
                'company_name': company_obj.get('name', ''),
                'street_address': location.get('street', ''),
                'city': location.get('city', {}).get('name', ''),
                'state_province': location.get('region', {}).get('name', '') or location.get('state', ''),
                'postal_code': location.get('postalCode', ''),
                'country': location.get('country', {}).get('name', ''),
                'phone_number': phone_number,
                'email': next((email['contactString'] for email in company_obj.get('emailAddresses', []) if email.get('contactString')), ''),
                'description': company_obj.get('description', ''),
                'linkedin_social_page': next((uri for uri in company_obj.get('allUris', []) if 'linkedin.com' in uri), '')
            }
            logger.info(f"Successfully fetched data for website: {website}")
            return JsonResponse(company_data)

        else:
            logger.warning(f"No company data found in the API response for website: {website}")
            return JsonResponse({'error': 'No company data found in the response'}, status=404)

    except requests.Timeout:
        logger.error(f"Request to Diffbot API timed out for website: {website}")
        return JsonResponse({'error': 'Request to Diffbot API timed out'}, status=504)
    except requests.RequestException as e:
        logger.error(f"Error fetching company data from Diffbot API: {e}")
        return JsonResponse({'error': f'Error processing page: {str(e)}'}, status=500)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    # Log completion of the view
    logger.info(f"fetch_company_data completed in {time.time() - start_time:.2f} seconds.")


@login_required
def search_companies(request):
    """
    View to search companies based on a query.

    This view searches for companies within the user's agency that match the
    search query. It returns the top 10 results that start with the query string.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.

    Returns:
        JsonResponse: Contains the search results as a list of company names and IDs.
    """
    logger.info("Entering search_companies view.")
    start_time = time.time()

    # Get the search query and user's agency
    query = request.GET.get('q', '')
    agency = request.user.agency
    logger.debug(f"Search query: '{query}' for agency: {agency}")

    # Perform the search on company names
    try:
        companies = Company.objects.filter(
            company_name__istartswith=query,
            agency=agency
        )[:10]
        logger.debug(f"Found {companies.count()} companies matching the query.")
    except Exception as e:
        logger.error(f"Error searching companies: {e}")
        companies = []

    # Prepare results for JSON response
    results = [{'id': company.id, 'text': company.company_name} for company in companies]

    logger.info(f"search_companies completed in {time.time() - start_time:.2f} seconds.")
    return JsonResponse({'results': results})


@login_required
def contact_detail(request, pk):
    """
    View to display the details of a specific contact.

    This view fetches the contact details based on the provided primary key (pk)
    and renders a template to display the contact's information.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the contact to be displayed.

    Returns:
        HttpResponse: Renders the contact_detail template with the contact's information.
    """
    logger.info(f"Entering contact_detail view for contact pk={pk}.")
    start_time = time.time()

    # Fetch the contact based on pk
    contact = get_object_or_404(Contact, pk=pk)
    logger.debug(f"Fetched contact: {contact.first_name} {contact.last_name}.")

    logger.info(f"contact_detail completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'crm/contact_detail.html', {'contact': contact})


@login_required
def add_contact(request, pk):
    """
    View to add a new contact to a company.

    This view allows users to create a new contact for a specific company by submitting
    a form. It handles both GET requests for displaying the blank form and POST requests
    for saving the new contact.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the company to which the contact will be added.

    Returns:
        HttpResponse: Renders the add_contact template with the form, or redirects
        to the company detail view on successful addition.
    """
    logger.info(f"Entering add_contact view for company pk={pk}.")
    start_time = time.time()

    # Fetch the company based on pk
    company = get_object_or_404(Company, pk=pk)
    logger.debug(f"Fetched company: {company.company_name} for adding contact.")

    # Handle form submission for adding a new contact
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.company = company
            contact.save()
            logger.info(f"Contact '{contact.first_name} {contact.last_name}' successfully added.")
            messages.success(request, f"Contact '{contact.first_name} {contact.last_name}' has been successfully added.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='contacts')
        else:
            logger.error(f"Form validation errors: {form.errors}")

    # Initialize the form for GET requests
    else:
        form = ContactForm()
        logger.debug("Initialized form for adding a new contact.")

    logger.info(f"add_contact completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'crm/add_contact.html', {'form': form, 'company': company})


@login_required
def edit_contact(request, pk):
    """
    View to edit the details of a specific contact.

    This view allows users to update the details of a contact by submitting a form.
    It handles both GET requests for displaying the form with current contact data,
    and POST requests for updating the data.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the contact to be edited.

    Returns:
        HttpResponse: Renders the edit_contact template with the form and contact details,
        or redirects to the company detail view on successful update.
    """
    logger.info(f"Entering edit_contact view for contact pk={pk}.")
    start_time = time.time()

    # Fetch the contact and its associated company
    contact = get_object_or_404(Contact, pk=pk)
    company = contact.company
    logger.debug(f"Fetched contact: {contact.first_name} {contact.last_name} for editing.")

    # Handle form submission for updating contact details
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            logger.info(f"Contact '{contact.first_name} {contact.last_name}' successfully updated.")
            messages.success(request, f"Contact '{contact.first_name} {contact.last_name}' has been successfully updated.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='contacts')
        else:
            logger.error(f"Form validation errors: {form.errors}")

    # Initialize the form with the current contact instance for GET requests
    else:
        form = ContactForm(instance=contact)
        logger.debug("Initialized form for contact editing.")

    logger.info(f"edit_contact completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'crm/edit_contact.html', {
        'form': form,
        'contact': contact,
        'company': company,
    })


@login_required
def confirm_delete_contact(request, pk):
    """
    View to confirm and delete a specific contact.

    This view displays a confirmation page for deleting a contact. If the user confirms
    by submitting a POST request, the contact is deleted from the database.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the contact to be deleted.

    Returns:
        HttpResponse: Redirects to the company detail view on successful deletion,
        or renders a confirmation page.
    """
    logger.info(f"Entering confirm_delete_contact view for contact pk={pk}.")
    start_time = time.time()

    # Fetch the contact and its associated company
    contact = get_object_or_404(Contact, pk=pk)
    company = contact.company
    logger.debug(f"Fetched contact: {contact.first_name} {contact.last_name} for deletion confirmation.")

    # Handle contact deletion upon POST request
    if request.method == 'POST':
        contact.delete()
        logger.info(f"Contact '{contact.first_name} {contact.last_name}' successfully deleted.")
        messages.success(request, f"Contact '{contact.first_name} {contact.last_name}' has been successfully deleted.")
        return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='contacts')

    # Render a confirmation page for GET requests
    logger.info(f"confirm_delete_contact completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'crm/confirm_delete_contact.html', {'contact': contact})


@login_required
def delete_contact_view(request, pk):
    """
    View to delete a specific contact after confirmation.

    This view displays a confirmation page for deleting a contact. If the user
    confirms the deletion by submitting a POST request with the correct contact name,
    the contact is deleted from the database.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the contact to be deleted.

    Returns:
        HttpResponse: Redirects to the company detail view on successful deletion,
        or renders a confirmation page if the name does not match.
    """
    logger.info(f"Entering delete_contact_view for contact pk={pk}.")
    start_time = time.time()

    # Fetch the contact and its associated company
    contact = get_object_or_404(Contact, pk=pk)
    company = contact.company
    logger.debug(f"Fetched contact: {contact.first_name} {contact.last_name} for deletion.")

    # Handle deletion upon POST request with name confirmation
    if request.method == "POST":
        confirmation_name = request.POST.get("confirmation_name")
        if confirmation_name == f"{contact.first_name} {contact.last_name}":
            contact.delete()
            logger.info(f"Contact '{contact.first_name} {contact.last_name}' successfully deleted.")
            messages.success(request, "Contact successfully deleted.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='contacts')
        else:
            logger.warning(f"Name confirmation failed for contact '{contact.first_name} {contact.last_name}'.")
            messages.error(request, "The contact name does not match.")

    # Render a confirmation page for GET requests
    logger.info(f"delete_contact_view completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'crm/confirm_delete_contact.html', {'contact': contact})


@login_required
def add_company_notes(request, pk):
    """
    View to add notes to a company.

    This view allows users to add notes for a specific company by submitting
    a form. If the company already has notes, it redirects to the edit notes view.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the company to which notes will be added.

    Returns:
        HttpResponse: Renders the add_company_notes template with the form,
        or redirects to the company detail view on successful addition.
    """
    logger.info(f"Entering add_company_notes view for company pk={pk}.")
    start_time = time.time()

    # Fetch the company and check if notes already exist
    company = get_object_or_404(Company, pk=pk)
    if hasattr(company, 'notes'):
        logger.info(f"Company '{company.company_name}' already has notes. Redirecting to edit.")
        return redirect('crm:edit_company_notes', pk=company.pk)

    # Handle form submission for adding new notes
    if request.method == 'POST':
        form = CompanyNotesForm(request.POST)
        if form.is_valid():
            notes = form.save(commit=False)
            notes.company = company
            notes.save()
            logger.info(f"Notes successfully added for company '{company.company_name}'.")
            messages.success(request, f"Notes for '{company.company_name}' have been successfully added.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='notes')
        else:
            logger.error(f"Form validation errors: {form.errors}")

    # Initialize the form for GET requests
    else:
        form = CompanyNotesForm()
        logger.debug("Initialized form for adding company notes.")

    context = {
        'form': form,
        'company': company,
    }

    logger.info(f"add_company_notes completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'crm/add_company_notes.html', context)


@login_required
def edit_company_notes(request, pk):
    """
    View to edit existing notes for a company.

    This view allows users to update the existing notes of a company by submitting
    a form. It handles both GET requests for displaying the form with current notes data,
    and POST requests for updating the notes.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the company whose notes will be edited.

    Returns:
        HttpResponse: Renders the edit_company_notes template with the form and notes details,
        or redirects to the company detail view on successful update.
    """
    logger.info(f"Entering edit_company_notes view for company pk={pk}.")
    start_time = time.time()

    # Fetch the company and its associated notes
    company = get_object_or_404(Company, pk=pk)
    company_notes = get_object_or_404(CompanyNotes, company=company)
    logger.debug(f"Fetched notes for company '{company.company_name}'.")

    # Handle form submission for updating notes
    if request.method == 'POST':
        form = CompanyNotesForm(request.POST, instance=company_notes)
        if form.is_valid():
            form.save()
            logger.info(f"Notes for company '{company.company_name}' successfully updated.")
            messages.success(request, f"Notes for '{company.company_name}' have been successfully updated.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='notes')
        else:
            logger.error(f"Form validation errors: {form.errors}")

    # Initialize the form with the current notes instance for GET requests
    else:
        form = CompanyNotesForm(instance=company_notes)
        logger.debug("Initialized form for editing company notes.")

    context = {
        'form': form,
        'company': company,
    }

    logger.info(f"edit_company_notes completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'crm/edit_company_notes.html', context)


@login_required
def add_transaction_fee(request, pk):
    """
    View to add a new transaction fee to a company.

    This view allows users to create a new transaction fee for a specific company
    by submitting a form. It handles both GET requests for displaying the blank form
    and POST requests for saving the new fee.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the company to which the transaction fee will be added.

    Returns:
        HttpResponse: Redirects to the company detail view on successful addition,
        or renders the company detail template with form errors.
    """
    logger.info(f"Entering add_transaction_fee view for company pk={pk}.")
    start_time = time.time()

    # Fetch the company based on pk
    company = get_object_or_404(Company, pk=pk)
    logger.debug(f"Fetched company: {company.company_name} for adding transaction fee.")

    # Handle form submission for adding a new transaction fee
    if request.method == 'POST':
        form = TransactionFeeForm(request.POST)
        if form.is_valid():
            fee = form.save(commit=False)
            fee.company = company
            fee.save()
            logger.info(f"Transaction fee successfully added to company '{company.company_name}'.")
            messages.success(request, f"Transaction fee has been successfully added to '{company.company_name}'.")
            # Redirect to the company detail view with 'notes' tab active
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='notes')
        else:
            logger.error(f"Form validation errors: {form.errors}")
            messages.error(request, "There was an error adding the transaction fee. Please correct the errors below.")

            # Render the response with form errors if submission fails
            context = {
                'company': company,
                'form': form,
                'transaction_fees': company.transaction_fees.all(),
                'contacts': company.contacts.all(),
                'company_notes': getattr(company, 'notes', None),
                'active_tab': 'fees',  # Show the tab relevant to fees
            }
            logger.info(f"add_transaction_fee completed with errors in {time.time() - start_time:.2f} seconds.")
            return render(request, 'crm/company_detail.html', context)

    # If not a POST request, redirect back to the notes tab
    logger.info(f"add_transaction_fee completed without POST request, redirecting to notes tab.")
    return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='notes')


@login_required
def edit_transaction_fee(request, pk):
    """
    View to edit an existing transaction fee.

    This view allows users to update an existing transaction fee by submitting a form.
    It handles both GET requests for displaying the form with current fee data, and
    POST requests for updating the fee.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the transaction fee to be edited.

    Returns:
        HttpResponse: Redirects to the company detail view on successful update,
        or renders the edit_transaction_fee template with form errors.
    """
    logger.info(f"Entering edit_transaction_fee view for fee pk={pk}.")
    start_time = time.time()

    # Fetch the transaction fee and its associated company
    fee = get_object_or_404(TransactionFee, pk=pk)
    company = fee.company
    logger.debug(f"Fetched transaction fee for company '{company.company_name}'.")

    # Handle form submission for updating the transaction fee
    if request.method == 'POST':
        form = TransactionFeeForm(request.POST, instance=fee)
        if form.is_valid():
            form.save()
            logger.info(f"Transaction fee for company '{company.company_name}' successfully updated.")
            messages.success(request, f"Transaction fee for '{company.company_name}' has been successfully updated.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='notes')
        else:
            logger.error(f"Form validation errors: {form.errors}")
            messages.error(request, "There was an error updating the transaction fee. Please try again.")

    # Initialize the form with the current fee instance for GET requests
    else:
        form = TransactionFeeForm(instance=fee)
        logger.debug("Initialized form for editing transaction fee.")

    context = {
        'form': form,
        'fee': fee,
        'company': company,
    }

    logger.info(f"edit_transaction_fee completed in {time.time() - start_time:.2f} seconds.")
    return render(request, 'crm/edit_transaction_fee.html', context)


@login_required
def delete_transaction_fee(request, pk):
    """
    View to delete a specific transaction fee.

    This view allows users to delete a transaction fee from a company. It handles
    the deletion upon POST request and redirects back to the company detail view.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.
        pk (int): The primary key of the transaction fee to be deleted.

    Returns:
        HttpResponse: Redirects to the company detail view on successful deletion.
    """
    logger.info(f"Entering delete_transaction_fee view for fee pk={pk}.")
    start_time = time.time()

    # Fetch the transaction fee and its associated company
    fee = get_object_or_404(TransactionFee, pk=pk)
    company_pk = fee.company.pk
    company_name = fee.company.company_name
    logger.debug(f"Fetched transaction fee for company '{company_name}' for deletion.")

    # Handle fee deletion upon POST request
    if request.method == 'POST':
        fee.delete()
        logger.info(f"Transaction fee for company '{company_name}' successfully deleted.")
        messages.success(request, f"Transaction fee for '{company_name}' has been successfully deleted.")
    
    # Redirect to the company detail view with 'notes' tab active
    logger.info(f"delete_transaction_fee completed in {time.time() - start_time:.2f} seconds.")
    return redirect('crm:company_detail_with_tab', pk=company_pk, active_tab='notes')