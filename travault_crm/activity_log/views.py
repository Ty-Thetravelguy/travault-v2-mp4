#activity_log/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from crm.models import Company
from .models import ActivityLog
from .forms import CallLogForm, EmailLogForm, MeetingLogForm, TicketForm, DealForm


@login_required
def activity_log(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk, agency=request.user.agency)
    activities = ActivityLog.objects.filter(company=company)
    context = {
        'company': company,
        'activities': activities,
    }
    return render(request, 'activity_log/activity_log.html', context)


@login_required
def log_call(request, pk):
    company = get_object_or_404(Company, pk=pk, agency=request.user.agency)
    if request.method == 'POST':
        form = CallLogForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.company = company
            activity.user = request.user
            activity.activity_type = 'call'
            activity.save()
            messages.success(request, 'Call logged successfully.')
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity')
    else:
        form = CallLogForm()
    
    return render(request, 'activity_log/log_call.html', {'form': form, 'company': company})

@login_required
def log_email(request, pk):
    company = get_object_or_404(Company, pk=pk, agency=request.user.agency)
    if request.method == 'POST':
        form = EmailLogForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.company = company
            activity.user = request.user
            activity.activity_type = 'email'
            activity.save()
            messages.success(request, 'Email logged successfully.')
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity')
    else:
        form = EmailLogForm()
    
    return render(request, 'activity_log/log_email.html', {'form': form, 'company': company})

@login_required
def log_meeting(request, pk):
    company = get_object_or_404(Company, pk=pk, agency=request.user.agency)
    if request.method == 'POST':
        form = MeetingLogForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.company = company
            activity.user = request.user
            activity.activity_type = 'meeting'
            activity.save()
            messages.success(request, 'Meeting logged successfully.')
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity')
    else:
        form = MeetingLogForm()
    
    return render(request, 'activity_log/log_meeting.html', {'form': form, 'company': company})

@login_required
def open_ticket(request, pk):
    company = get_object_or_404(Company, pk=pk, agency=request.user.agency)
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.company = company
            activity.user = request.user
            activity.activity_type = 'ticket'
            activity.save()
            messages.success(request, 'Ticket opened successfully.')
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity')
    else:
        form = TicketForm()
    
    return render(request, 'activity_log/open_ticket.html', {'form': form, 'company': company})

@login_required
def start_deal(request, pk):
    company = get_object_or_404(Company, pk=pk, agency=request.user.agency)
    if request.method == 'POST':
        form = DealForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.company = company
            activity.user = request.user
            activity.activity_type = 'deal'
            activity.save()
            messages.success(request, 'Deal started successfully.')
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity')
    else:
        form = DealForm()
    
    return render(request, 'activity_log/start_deal.html', {'form': form, 'company': company})