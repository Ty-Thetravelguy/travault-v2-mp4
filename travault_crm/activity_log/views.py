from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Meeting
from .forms import MeetingForm
from crm.models import Company, Contact
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def log_meeting(request, pk):
    company = get_object_or_404(Company, pk=pk)

    if request.method == 'POST':
        form = MeetingForm(request.POST, company=company, creator=request.user)  # Passing company and creator
        if form.is_valid():
            try:
                meeting = form.save()  # commit=True by default
                messages.success(request, "Meeting logged successfully!")
                return redirect('crm:company_detail', pk=company.pk)
            except Exception as e:
                form.add_error(None, f"An unexpected error occurred: {str(e)}")
                messages.error(request, f"An unexpected error occurred while saving the meeting: {str(e)}")
        else:
            messages.error(request, "There were errors in your submission. Please correct them below.")
    else:
        form = MeetingForm(company=company, creator=request.user)  # Passing company and creator

    context = {
        'form': form,
        'company': company,
    }
    return render(request, 'activity_log/log_meeting.html', context)

@login_required
def search_attendees(request):
    query = request.GET.get('q', '')
    company_pk = request.GET.get('company_pk')

    if not company_pk:
        return JsonResponse({'results': []})

    company = get_object_or_404(Company, pk=company_pk)
    agency = request.user.agency

    # Search for company contacts
    contacts = Contact.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query),
        company=company
    )[:10]

    # Search for users in the agency
    users = User.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query),
        agency=agency
    )[:10]

    # Prepare results, contacts first, then users
    results = []

    for contact in contacts:
        results.append({
            'id': f'contact_contact_{contact.pk}',  # Correct prefix
            'name': f"{contact.first_name} {contact.last_name} (Contact)"
        })

    for user in users:
        results.append({
            'id': f'contact_user_{user.pk}',  # Correct prefix
            'name': f"{user.first_name} {user.last_name} (User)"
        })

    return JsonResponse({'results': results})

@login_required
def view_meeting(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    company = meeting.company

    attendees = list(meeting.attendees.all()) + list(meeting.company_contacts.all())

    context = {
        'meeting': meeting,
        'company': company,
        'attendees': attendees
    }
    return render(request, 'activity_log/view_meeting.html', context)
