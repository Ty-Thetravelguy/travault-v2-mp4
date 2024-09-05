from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import requests
import os
from .models import Company
from .forms import CompanyForm
from urllib.parse import quote

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
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.agency = agency  # Link the company to the user's agency
            company.save()
            return redirect('crm:index')
    else:
        form = CompanyForm()
    
    return render(request, 'crm/add_company.html', {'form': form})


def fetch_company_data(request):
    website = request.GET.get('website')
    if website:
        # Fetch API key from environment variable
        api_key = os.environ.get('DIFFBOT_API_KEY')
        if not api_key:
            return JsonResponse({'error': 'API key is missing'}, status=500)
        
        # URL encode the website URL
        encoded_website = quote(website)
        
        # Make API call to Diffbot
        response = requests.get(f'https://api.diffbot.com/v3/analyze?url={encoded_website}&token={api_key}')
        
        # Check for API errors
        if response.status_code != 200:
            return JsonResponse({'error': 'Error processing page.'}, status=response.status_code)
        
        # Extract data from the API response
        data = response.json()
        
        # Extract required data fields from the API response
        company_data = {
            'company_name': data.get('name'),
            'address': data.get('address'),
            'email': data.get('email'),
            'industry': data.get('industry'),
            'description': data.get('description'),
            'linkedin_social_page': data.get('linkedin'),
        }
        
        return JsonResponse(company_data)

    return JsonResponse({'error': 'Website not provided'}, status=400)
