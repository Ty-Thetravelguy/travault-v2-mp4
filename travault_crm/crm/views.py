#crm/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import requests
from .models import Company
from .forms import CompanyForm
from urllib.parse import quote
from django.conf import settings
from django.db.models import Q


@login_required
def crm_index(request):
    # Fetch companies linked to the logged-in user's agency
    agency = request.user.agency
    companies = Company.objects.filter(agency=agency)

    return render(request, 'crm/index.html', {'companies': companies})

@login_required
def company_detail(request, company_id):
    # Fetch the company object based on the provided company_id and linked to the user's agency
    agency = request.user.agency
    company = get_object_or_404(Company, id=company_id, agency=agency)
    
    # Fetch all companies to keep the company list visible as well
    companies = Company.objects.filter(agency=agency)

    # Pass both the specific company and the list of companies
    return render(request, 'crm/index.html', {'companies': companies, 'selected_company': company})


@login_required
def add_company(request):
    agency = request.user.agency  # Get the agency of the logged-in user

    if request.method == 'POST':
        form = CompanyForm(request.POST, agency=agency)  # Pass agency to form
        if form.is_valid():
            company = form.save(commit=False)
            company.agency = agency 
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
                company_data = {
                    'company_name': company_obj.get('name', ''),
                    'street': location.get('street', ''),
                    'city': location.get('city', {}).get('name', ''),
                    'country': location.get('country', {}).get('name', ''),
                    'postcode': location.get('postalCode', ''),
                    'phone_number': company_obj.get('phoneNumbers', [{}])[0].get('number', ''),
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