# activity_log/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from .forms import MeetingForm
from crm.models import Company, Contact
from django.db.models import Q

User = get_user_model()

@login_required
def log_meeting(request, pk):
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'POST':
        form = MeetingForm(request.POST, company=company)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.creator = request.user
            meeting.company = company
            meeting.save()
            form.save_m2m()  # Save the many-to-many attendees fields
            return redirect('crm:company_detail', pk=company.pk)
    else:
        form = MeetingForm(company=company)
    
    context = {
        'form': form,
        'company': company,
    }
    return render(request, 'activity_log/log_meeting.html', context)


def search_attendees(request):
    query = request.GET.get('q', '')
    company_pk = request.GET.get('company_pk')
    
    # Ensure we get the company
    if company_pk:
        company = Contact.objects.filter(company_id=company_pk)
    else:
        company = Contact.objects.none()

    agency = request.user.agency

    # Search for contacts in the company
    contacts = Contact.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query),
        company__pk=company_pk
    )[:10]

    # Search for users in the agency
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
