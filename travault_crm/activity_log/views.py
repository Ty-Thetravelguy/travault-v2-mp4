# activity_log/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Q
from .forms import MeetingForm
from crm.models import Company, Contact
from .models import Meeting
from django.contrib import messages
import datetime



User = get_user_model()

@login_required
def log_meeting(request, pk):
    company = get_object_or_404(Company, pk=pk)
    agency = request.user.agency

    if request.method == 'POST':
        form = MeetingForm(request.POST, company=company, agency=agency)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.creator = request.user
            meeting.agency = agency
            meeting.save()
            meeting.associated_companies.add(company)
            form.save_m2m()  # This will save the attendees
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity_log')
    else:
        form = MeetingForm(company=company, agency=agency)
    
    context = {
        'form': form,
        'company': company,
    }
    return render(request, 'activity_log/log_meeting.html', context)


def search_attendees(request):
    query = request.GET.get('q', '')
    company_pk = request.GET.get('company_pk')
    agency = request.user.agency

    company = Company.objects.get(pk=company_pk)
    
    contacts = Contact.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query),
        company=company
    )[:10]
    
    users = User.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query),
        agency=agency
    )[:10]

    results = []
    for contact in contacts:
        results.append({
            'pk': contact.pk,
            'name': f"{contact.first_name} {contact.last_name}",
            'model': 'contact'
        })
    for user in users:
        results.append({
            'pk': user.pk,
            'name': f"{user.first_name} {user.last_name}",
            'model': 'user'
        })

    return JsonResponse(results, safe=False)


@login_required
def view_meeting(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    company = meeting.associated_companies.first()
    return render(request, 'activity_log/view_meeting.html', {'meeting': meeting, 'company': company})
