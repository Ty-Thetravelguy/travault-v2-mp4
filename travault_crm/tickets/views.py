from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TicketSubject,Ticket
from .forms import TicketForm
from crm.models import Company, Contact
from django.shortcuts import get_object_or_404
from dal import autocomplete
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@login_required
def view_tickets(request):
    return render(request, 'tickets/view_tickets.html')

@login_required
def ticket_subject_autocomplete(request):
    query = request.GET.get('q', '')
    subjects = TicketSubject.objects.filter(subject__icontains=query)[:10]
    data = [{'id': subject.id, 'text': subject.subject} for subject in subjects]
    return JsonResponse(data, safe=False)

@login_required
@require_POST
def create_ticket_subject(request):
    subject = request.POST.get('subject')
    new_subject, created = TicketSubject.objects.get_or_create(subject=subject)
    return JsonResponse({'id': new_subject.id, 'subject': new_subject.subject})


@login_required
def open_ticket(request, company_id):
    # Fetch the company by its ID
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.company = company  # Automatically associate the ticket with the selected company
            ticket.owner = request.user  # Assign the ticket to the current user
            ticket.agency = request.user.agency  # Assign the ticket to the user's agency
            ticket.save()
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        # Pre-fill the company field in the form
        form = TicketForm(initial={'company': company})

    return render(request, 'tickets/open_ticket.html', {'form': form, 'company': company})

def ticket_list(request):
    # Filter tickets based on the agency of the logged-in user
    tickets = Ticket.objects.filter(agency=request.user.agency)
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})

def ticket_detail(request, pk):
    # Ensure the ticket belongs to the user's agency
    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})