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

logger = logging.getLogger(__name__)
User = get_user_model()

@login_required
def crm_index(request):
    agency = request.user.agency
    companies = Company.objects.filter(agency=agency).order_by('-create_date')
    company_owners = User.objects.filter(agency=agency, user_type__in=['admin', 'sales'])

    context = {
        'companies': companies,
        'company_type_choices': COMPANY_TYPE_CHOICES,
        'company_owners': company_owners,
    }

    return render(request, 'crm/index.html', context)

@login_required
def company_detail(request, pk, active_tab='details'):
    company = get_object_or_404(Company, pk=pk, agency=request.user.agency)
    
    # Fetch all companies to keep the company list visible
    companies = Company.objects.filter(agency=request.user.agency)

    # Sort contacts with primary contacts first
    contacts = company.contacts.annotate(
        is_primary=Case(
            When(is_primary_contact=True, then=True),
            default=False,
            output_field=BooleanField(),
        )
    ).order_by('-is_primary', 'first_name', 'last_name')

    travel_bookers = contacts.filter(is_travel_booker_contact=True)
    vip_travellers = contacts.filter(is_vip_traveller_contact=True)
    
    # Fetch company notes, handle if not exists
    try:
        company_notes = company.notes
        logger.debug(f"Company notes found for company {company.pk}: {company_notes}")
    except CompanyNotes.DoesNotExist:
        company_notes = None
        logger.debug(f"No company notes found for company {company.pk}")

    # Fetch transaction fees
    transaction_fees = company.transaction_fees.all()
    
    # Create a blank form for adding fees
    fee_form = TransactionFeeForm()

    # Create a dictionary of edit forms for each fee
    edit_forms = {fee.id: TransactionFeeForm(instance=fee) for fee in transaction_fees}

    context = {
        'company': company,
        'companies': companies,
        'selected_company': company,
        'contacts': contacts,
        'travel_bookers': travel_bookers,
        'vip_travellers': vip_travellers,
        'company_notes': company_notes,
        'transaction_fees': transaction_fees,
        'fee_form': fee_form,  # Add form for creating new transaction fees
        'edit_forms': edit_forms,  # Edit forms for existing transaction fees
        'active_tab': active_tab or 'details',  # Set a default tab if not provided
    }
    
    logger.debug(f"Context being passed to template: {context}")
    return render(request, 'crm/company_detail.html', context)

@login_required
def edit_company(request, pk):
    company = get_object_or_404(Company, pk=pk, agency=request.user.agency)
    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company, agency=request.user.agency)
        if form.is_valid():
            company = form.save(commit=False)
            company.save()  # Save the company instance first
            form.save_m2m()  # Save many-to-many relationships to handle linked companies
            messages.success(request, f"Company '{company.company_name}' has been successfully updated.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='details')  # Include active_tab if needed
    else:
        # Properly initialize the form with the current company instance
        form = CompanyForm(instance=company, agency=request.user.agency)
    
    context = {
        'form': form,
        'company': company,
    }
    return render(request, 'crm/edit_company.html', context)


@login_required
def delete_company(request, pk):
    company = get_object_or_404(Company, pk=pk, agency=request.user.agency)
    if request.method == 'POST':
        company.delete()
        messages.success(request, f"Company '{company_name}' has been successfully deleted.")
        return redirect('crm:index')
    return render(request, 'crm/delete_company_confirm.html', {'company': company})


@login_required
def add_company(request):
    agency = request.user.agency 

    if request.method == 'POST':
        form = CompanyForm(request.POST, agency=agency)  
        if form.is_valid():
            company = form.save(commit=False)
            company.agency = agency 
            company.save()  
            form.save_m2m()
            messages.success(request, f"Company '{company.company_name}' has been successfully added.")
            return redirect('crm:index')
    else:
        form = CompanyForm(agency=agency)  # Pass agency to form

    return render(request, 'crm/add_company.html', {'form': form})

@login_required
def fetch_company_data(request):
    website = request.GET.get('website', '').strip()
    if website:
        api_key = settings.DIFFBOT_API_KEY
        if not api_key:
            return JsonResponse({'error': 'API key is missing'}, status=500)
        
        encoded_website = quote(website)
        
        full_url = f'https://api.diffbot.com/v3/analyze?url={encoded_website}&token={api_key}&timeout=50000'
        
        try:
            response = requests.get(full_url, timeout=60)
            
            if response.status_code != 200:
                return JsonResponse({'error': f'Error processing page: {response.text}'}, status=response.status_code)
            
            data = response.json()
            
            if 'objects' in data and len(data['objects']) > 0:
                company_obj = data['objects'][0]
                location = company_obj.get('locations', [{}])[0]
                
                # Extract phone number using only 'string'
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
                
                return JsonResponse(company_data)
            else:
                return JsonResponse({'error': 'No company data found in the response'}, status=404)
        
        except requests.Timeout:
            return JsonResponse({'error': 'Request to Diffbot API timed out'}, status=504)
        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Website not provided'}, status=400)

@login_required
def search_companies(request):
    query = request.GET.get('q', '')
    agency = request.user.agency

    companies = Company.objects.filter(
        company_name__istartswith=query,
        agency=agency
    )[:10]
    
    results = [{'id': company.id, 'text': company.company_name} for company in companies]
    return JsonResponse({'results': results})


@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, 'crm/contact_detail.html', {'contact': contact})


@login_required
def add_contact(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.company = company
            contact.save()
            messages.success(request, f"Contact '{contact.first_name} {contact.last_name}' has been successfully added.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='contacts')
    else:
        form = ContactForm()
    
    return render(request, 'crm/add_contact.html', {'form': form, 'company': company})


@login_required
def edit_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    company = contact.company

    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            messages.success(request, f"Contact '{contact.first_name} {contact.last_name}' has been successfully updated.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='contacts')
    else:
        form = ContactForm(instance=contact)

    return render(request, 'crm/edit_contact.html', {
        'form': form,
        'contact': contact,
        'company': company,
    })


@login_required
def confirm_delete_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    company = contact.company

    if request.method == 'POST':
        contact.delete()
        messages.success(request, f"Contact '{contact.first_name} {contact.last_name}' has been successfully deleted.")
        return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='contacts')

    # Render a confirmation page if the request is GET
    return render(request, 'crm/confirm_delete_contact.html', {'contact': contact})


@login_required
def delete_contact_view(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    company = contact.company
    if request.method == "POST":
        confirmation_name = request.POST.get("confirmation_name")
        if confirmation_name == contact.first_name + " " + contact.last_name:
            contact.delete()
            messages.success(request, "Contact successfully deleted.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='contacts')
        else:
            messages.error(request, "The contact name does not match.")
    return render(request, 'crm/confirm_delete_contact.html', {'contact': contact})


@login_required
def add_company_notes(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if hasattr(company, 'notes'):
        return redirect('crm:edit_company_notes', pk=company.pk)

    if request.method == 'POST':
        form = CompanyNotesForm(request.POST)
        if form.is_valid():
            notes = form.save(commit=False)
            notes.company = company
            notes.save()
            messages.success(request, f"Notes for '{company.company_name}' have been successfully added.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='notes')
    else:
        form = CompanyNotesForm()

    context = {
        'form': form,
        'company': company,
    }
    return render(request, 'crm/add_company_notes.html', context)


@login_required
def edit_company_notes(request, pk):
    company = get_object_or_404(Company, pk=pk)
    company_notes = get_object_or_404(CompanyNotes, company=company)

    if request.method == 'POST':
        form = CompanyNotesForm(request.POST, instance=company_notes)
        if form.is_valid():
            form.save()
            messages.success(request, f"Notes for '{company.company_name}' have been successfully updated.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='notes')
    else:
        form = CompanyNotesForm(instance=company_notes)

    context = {
        'form': form,
        'company': company,
    }
    return render(request, 'crm/edit_company_notes.html', context)


@login_required
def add_transaction_fee(request, pk):
    company = get_object_or_404(Company, pk=pk)
    if request.method == 'POST':
        form = TransactionFeeForm(request.POST)
        if form.is_valid():
            fee = form.save(commit=False)
            fee.company = company
            fee.save()
            messages.success(request, f"Transaction fee has been successfully added to '{company.company_name}'.")
            # Redirect to the correct tab
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='fees')
        else:
            # Log form errors and render the template with errors
            logger.error(f"Form errors: {form.errors}")
            messages.error(request, "There was an error adding the transaction fee. Please correct the errors below.")
            # Return a rendered response with the correct context
            return render(request, 'crm/company_detail.html', {
                'company': company,
                'form': form,
                'transaction_fees': company.transaction_fees.all(),
                'contacts': company.contacts.all(),
                'company_notes': getattr(company, 'notes', None),
                'active_tab': 'fees',
            })

    # If not a POST request, redirect back to the fees tab
    return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='fees')


@login_required
def edit_transaction_fee(request, pk):
    fee = get_object_or_404(TransactionFee, pk=pk)
    company = fee.company  # Retrieve the company associated with the transaction fee

    if request.method == 'POST':
        form = TransactionFeeForm(request.POST, instance=fee)
        if form.is_valid():
            form.save()
            messages.success(request, f"Transaction fee for '{company.company_name}' has been successfully updated.")
        else:
            messages.error(request, "There was an error updating the transaction fee. Please try again.")
        
        # Correct redirect to use the company instance properly
        return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='notes')

    else:
        form = TransactionFeeForm(instance=fee)

    context = {
        'form': form,
        'fee': fee,
        'company': company,
    }

    return render(request, 'crm/edit_transaction_fee.html', context)

@login_required
def delete_transaction_fee(request, pk):
    fee = get_object_or_404(TransactionFee, pk=pk)
    company_pk = fee.company.pk
    company_name = fee.company.company_name
    if request.method == 'POST':
        fee.delete()
        messages.success(request, f"Transaction fee for '{company_name}' has been successfully deleted.")
    return redirect('crm:company_detail_with_tab', pk=company_pk, active_tab='notes')
