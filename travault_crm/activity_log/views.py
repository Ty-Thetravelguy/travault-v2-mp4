# activity_log/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import MeetingForm
from crm.models import Company
from .models import Meeting
from django.contrib import messages
import datetime

@login_required
def log_meeting(request, pk):
    company = get_object_or_404(Company, pk=pk, agency=request.user.agency)

    if request.method == 'POST':
        form = MeetingForm(request.POST, company=company)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.creator = request.user
            meeting.agency = request.user.agency  # Set the agency
            meeting.save()
            form.save_m2m()
            meeting.associated_companies.add(company)
            # Add linked companies if any
            linked_companies = company.linked_companies.all()
            for linked_company in linked_companies:
                meeting.associated_companies.add(linked_company)
            messages.success(request, "Meeting has been logged successfully.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity_log')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        initial_data = {
            'date': datetime.date.today(),
            'time': datetime.datetime.now().time(),
        }
        form = MeetingForm(initial=initial_data, company=company)
    context = {
        'form': form,
        'company': company,
    }
    return render(request, 'activity_log/log_meeting.html', context)


@login_required
def view_meeting(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    company = meeting.associated_companies.first()
    return render(request, 'activity_log/view_meeting.html', {'meeting': meeting, 'company': company})