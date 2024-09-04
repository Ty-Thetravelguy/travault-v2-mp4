from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Company

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
