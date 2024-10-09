from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TicketSubject,Ticket
from .forms import TicketForm
from crm.models import Company
from django.shortcuts import get_object_or_404
from dal import autocomplete
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from .models import TicketSubject
from django.db.models import Count
from django.db.models import ProtectedError
from django.db.models.functions import Lower
from agencies.models import CustomUser  # Import your custom user model


@login_required
def view_tickets(request):
    tickets = Ticket.objects.filter(agency=request.user.agency).order_by('-created_at')
    return render(request, 'tickets/view_tickets.html', {'tickets': tickets})

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
def manage_subjects(request):
    subjects = TicketSubject.objects.annotate(ticket_count=Count('ticket')).order_by(Lower('subject'))
    return render(request, 'tickets/manage_subjects.html', {'subjects': subjects})

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
            'created': created,
            'redirect': reverse('tickets:manage_subjects')
        })
    else:
        messages.error(request, "No subject provided. Please enter a subject.")
        return JsonResponse({'error': 'No subject provided'}, status=400)

@login_required
@require_POST
def update_subject(request, subject_id):
    try:
        subject = TicketSubject.objects.get(id=subject_id)
        new_subject_name = request.POST.get('subject')
        if new_subject_name:
            subject.subject = new_subject_name
            subject.save()
            messages.success(request, f"Subject updated successfully to '{new_subject_name}'.")
            return JsonResponse({'success': True})
        else:
            messages.error(request, "No subject name provided.")
            return JsonResponse({'success': False, 'error': 'No subject name provided'}, status=400)
    except TicketSubject.DoesNotExist:
        messages.error(request, "Subject not found.")
        return JsonResponse({'success': False, 'error': 'Subject not found'}, status=404)

@login_required
@require_POST
def delete_subject(request, subject_id):
    try:
        subject = TicketSubject.objects.get(id=subject_id)
        
        # Check if there are any tickets associated with this subject
        if Ticket.objects.filter(subject=subject).exists():
            return JsonResponse({
                'success': False, 
                'error': 'Cannot delete this subject as it has tickets associated with it.'
            }, status=400)
        
        subject_name = subject.subject
        subject.delete()
        messages.success(request, f"Subject '{subject_name}' has been deleted.")
        return JsonResponse({'success': True})
    except TicketSubject.DoesNotExist:
        messages.error(request, "Subject not found.")
        return JsonResponse({'success': False, 'error': 'Subject not found'}, status=404)
    except ProtectedError:
        messages.error(request, "Cannot delete this subject as it is referenced by other parts of the system.")
        return JsonResponse({
            'success': False, 
            'error': 'Cannot delete this subject as it is referenced by other parts of the system.'
        }, status=400)

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

                        # Send email to the received_from user
            if ticket.received_from:
                subject = f'New Ticket Created: #{ticket.pk}'
                ticket_url = request.build_absolute_uri(reverse('tickets:ticket_detail', args=[ticket.pk]))
                html_message = render_to_string('tickets/email/ticket_created_email.html', {
                    'ticket': ticket,
                    'ticket_url': ticket_url
                })
                plain_message = strip_tags(html_message)
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = ticket.received_from.email

                send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

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

def preview_ticket_email(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)
    ticket_url = request.build_absolute_uri(reverse('tickets:ticket_detail', args=[ticket.pk]))
    
    context = {
        'ticket': ticket,
        'ticket_url': ticket_url,
    }
    
    return render(request, 'tickets/email/ticket_created_email.html', context)

@login_required
def delete_ticket_confirm(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)
    
    # Check if the user is an admin
    if request.user.user_type != 'admin':
        messages.error(request, "You don't have permission to delete tickets.")
        return redirect('tickets:ticket_detail', pk=ticket.pk)
    
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation')
        if confirmation == str(ticket.pk):
            ticket_number = ticket.pk 
            ticket.delete()
            messages.success(request, f"Ticket #{ticket_number} has been successfully deleted.")
            return redirect('tickets:view_tickets')
        else:
            messages.error(request, "Incorrect ticket number. Deletion cancelled.")
    
    return render(request, 'tickets/delete_ticket_confirm.html', {'ticket': ticket})

@login_required
@require_POST
def update_ticket_field(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)
    field = request.POST.get('field')
    value = request.POST.get('value')

    if field not in ['owner', 'received_from', 'priority', 'status']:
        return JsonResponse({'success': False, 'error': 'Invalid field'}, status=400)

    try:
        if field in ['owner', 'received_from']:
            user = get_object_or_404(CustomUser, pk=value, agency=request.user.agency)
            setattr(ticket, field, user)
            field_value = user.get_full_name() or user.username
        else:
            setattr(ticket, field, value)
            field_value = value
        
        ticket.save()
        
        message = f"Ticket #{ticket.pk} {field.replace('_', ' ')} updated to {field_value}."
        messages.success(request, message)
        
        return JsonResponse({'success': True, 'message': message})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)
    agency_users = CustomUser.objects.filter(agency=request.user.agency)
    status_choices = ['open', 'in_progress', 'closed']  # Add more as needed
    context = {
        'ticket': ticket,
        'agency_users': agency_users,
        'status_choices': status_choices,
    }
    return render(request, 'tickets/ticket_detail.html', context)

@login_required
def edit_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)
    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket, agency=request.user.agency)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ticket updated successfully.')
            return redirect('tickets:ticket_detail', pk=ticket.pk)
    else:
        form = TicketForm(instance=ticket, agency=request.user.agency)
    
    return render(request, 'tickets/edit_ticket.html', {'form': form, 'ticket': ticket})