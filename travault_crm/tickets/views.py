from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TicketSubject,Ticket
from .forms import TicketForm
from crm.models import Company, Contact
from django.shortcuts import get_object_or_404
from dal import autocomplete
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages



@login_required
def view_tickets(request):
    return render(request, 'tickets/view_tickets.html')

class TicketSubjectAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return TicketSubject.objects.none()

        qs = TicketSubject.objects.all()

        if self.q:
            qs = qs.filter(subject__icontains=self.q)

        return qs

ticket_subject_autocomplete = TicketSubjectAutocomplete.as_view()

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
    if subject:
        new_subject, created = TicketSubject.objects.get_or_create(subject=subject)
        if created:
            messages.success(request, f"New ticket subject '{subject}' has been created.")
        else:
            messages.info(request, f"Ticket subject '{subject}' already exists.")
        return JsonResponse({
            'id': new_subject.id, 
            'subject': new_subject.subject,
            'created': created
        })
    else:
        messages.error(request, "No subject provided. Please enter a subject.")
        return JsonResponse({'error': 'No subject provided'}, status=400)


@login_required
def open_ticket(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    
    if request.method == 'POST':
        form = TicketForm(request.POST, agency=request.user.agency)
        if form.is_valid():
            print("Form is valid")
            ticket = form.save(commit=False)
            ticket.company = company
            ticket.owner = request.user
            ticket.agency = request.user.agency
            ticket.save()
            messages.success(request, f"Ticket #{ticket.id} has been successfully created.")
            return redirect('tickets:ticket_detail', pk=ticket.id)
        else:
            messages.error(request, "There was an error creating the ticket. Please check the form and try again.")
    else:
        form = TicketForm(initial={'company': company}, agency=request.user.agency)

    return render(request, 'tickets/open_ticket.html', {'form': form, 'company': company})

def ticket_list(request):
    # Filter tickets based on the agency of the logged-in user
    tickets = Ticket.objects.filter(agency=request.user.agency)
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})

def ticket_detail(request, pk):
    # Ensure the ticket belongs to the user's agency
    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})
