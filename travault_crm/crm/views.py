#crm/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
import requests
from .models import Company, COMPANY_TYPE_CHOICES
from .forms import CompanyForm
from urllib.parse import quote
from django.conf import settings
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@login_required
def crm_index(request):
    agency = request.user.agency
    companies = Company.objects.filter(agency=agency).order_by('-create_date')
    company_owners = User.objects.filter(agency=agency, user_type__in=['admin', 'sales'])

    print(f"Number of companies fetched: {companies.count()}")  # Debug print

    context = {
        'companies': companies,
        'company_type_choices': COMPANY_TYPE_CHOICES,
        'company_owners': company_owners,
    }

    return render(request, 'crm/index.html', context)

@login_required
def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk, agency=request.user.agency)
    
    # Fetch all companies to keep the company list visible as well
    companies = Company.objects.filter(agency=request.user.agency)

    context = {
        'company': company,
        'companies': companies,
        'selected_company': company
    }
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
            return redirect('crm:company_detail', pk=company.pk)
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
