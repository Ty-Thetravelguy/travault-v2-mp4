#activity_log/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from crm.models import Company
from .models import ActivityLog
from .forms import ActivityLogForm

@login_required
def activity_log(request, company_pk):
    company = get_object_or_404(Company, pk=company_pk, agency=request.user.agency)
    activities = ActivityLog.objects.filter(company=company)

    if request.method == 'POST':
        form = ActivityLogForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.company = company
            activity.user = request.user
            activity.save()
            messages.success(request, 'Activity logged successfully.')
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity')
    else:
        form = ActivityLogForm()

    context = {
        'company': company,
        'activities': activities,
        'form': form,
    }
    return render(request, 'activity_log/activity_log.html', context)