from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Ticket
from .forms import TicketForm
from crm.models import Company, Contact
from django.shortcuts import get_object_or_404

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