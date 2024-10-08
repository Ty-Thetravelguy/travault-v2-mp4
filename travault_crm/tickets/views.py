from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TicketSubject,Ticket, TicketAction
from .forms import TicketForm
from crm.models import Company
from django.shortcuts import get_object_or_404
from dal import autocomplete
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from .models import TicketSubject
from django.db.models import Count
from django.db.models import ProtectedError
from django.db.models.functions import Lower
from agencies.models import CustomUser 
from .utils import send_ticket_email
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.forms.models import model_to_dict



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
            ticket = form.save(commit=False)
            ticket.company = company
            ticket.owner = request.user
            ticket.agency = request.user.agency
            ticket.save()

            messages.success(request, f"Ticket #{ticket.id} has been successfully created.")

            # Send email notification
            send_ticket_email(request, ticket, 'created')

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

@require_POST
@login_required
def update_ticket_field(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)
    field = request.POST.get('field')
    value = request.POST.get('value')

    valid_fields = ['owner', 'received_from', 'priority', 'status']

    if field not in valid_fields:
        return JsonResponse({'success': False, 'error': 'Invalid field'}, status=400)

    try:
        old_value = getattr(ticket, field)
        field_object = Ticket._meta.get_field(field)

        if field in ['owner', 'received_from']:
            user = get_object_or_404(CustomUser, pk=value, agency=request.user.agency)
            setattr(ticket, field, user)
            new_value_display = user.get_full_name() or user.username
            old_value_display = old_value.get_full_name() if old_value else 'None'
        else:
            setattr(ticket, field, value)
            new_value_display = dict(field_object.choices).get(value, value)
            old_value_display = dict(field_object.choices).get(old_value, old_value)

        ticket.save()

        update_message = f"{field.replace('_', ' ').capitalize()} updated from '{old_value_display}' to '{new_value_display}'."

        # Create a TicketAction for the update
        TicketAction.objects.create(
            ticket=ticket,
            action_type='update',
            details=update_message,
            created_by=request.user
        )

        # Send update email
        additional_context = {'update_message': update_message}
        send_ticket_email(request, ticket, 'updated', additional_context)

        messages.success(request, update_message)
        return JsonResponse({'success': True, 'message': update_message})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)
    agency_users = CustomUser.objects.filter(agency=request.user.agency)
    status_choices = ['open', 'in_progress', 'closed'] 
    actions = ticket.actions.all()
    context = {
        'ticket': ticket,
        'agency_users': agency_users,
        'status_choices': status_choices,
        'actions': actions,
        'ticket_action_types': TicketAction.ACTION_TYPES,
    }
    return render(request, 'tickets/ticket_detail.html', context)

@login_required
def edit_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)
    if request.method == 'POST':
        old_values = model_to_dict(ticket)
        form = TicketForm(request.POST, instance=ticket, agency=request.user.agency)
        if form.is_valid():
            updated_ticket = form.save()
            messages.success(request, 'Ticket updated successfully.')

            # Compare old and new values
            new_values = model_to_dict(updated_ticket)
            changes = []
            for field in form.changed_data:
                old_value = old_values.get(field)
                new_value = new_values.get(field)
                if old_value != new_value:
                    # Handle ForeignKey fields
                    field_object = Ticket._meta.get_field(field)
                    if isinstance(field_object, models.ForeignKey):
                        old_value_display = str(field_object.related_model.objects.get(pk=old_value)) if old_value else 'None'
                        new_value_display = str(field_object.related_model.objects.get(pk=new_value)) if new_value else 'None'
                    else:
                        old_value_display = dict(field_object.choices).get(old_value, old_value)
                        new_value_display = dict(field_object.choices).get(new_value, new_value)

                    changes.append(f"{field.replace('_', ' ').capitalize()} changed from '{old_value_display}' to '{new_value_display}'")

            if changes:
                update_message = "\n".join(changes)

                # Create a TicketAction to record the update
                TicketAction.objects.create(
                    ticket=updated_ticket,
                    action_type='update',
                    details=update_message,
                    created_by=request.user
                )

                # Send update email
                additional_context = {'update_message': update_message}
                send_ticket_email(request, updated_ticket, 'updated', additional_context)

            return redirect('tickets:ticket_detail', pk=updated_ticket.pk)
    else:
        form = TicketForm(instance=ticket, agency=request.user.agency)

    return render(request, 'tickets/edit_ticket.html', {'form': form, 'ticket': ticket})

@require_POST
@login_required
def add_ticket_action(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)
    action_type = request.POST.get('action_type')
    details = request.POST.get('details')

    if action_type and details:
        action = TicketAction.objects.create(
            ticket=ticket,
            action_type=action_type,
            details=details,
            created_by=request.user
        )
        messages.success(request, f"Action '{dict(TicketAction.ACTION_TYPES)[action_type]}' added successfully.")

        # Send action added email
        additional_context = {'action': action}
        send_ticket_email(request, ticket, 'action_added', additional_context)

    else:
        messages.error(request, "Invalid data. Please provide action type and details.")

    return redirect('tickets:ticket_detail', pk=pk)

@login_required
def edit_ticket_action(request, action_id):
    action = get_object_or_404(TicketAction, id=action_id, ticket__agency=request.user.agency)
    if request.method == 'POST':
        action_type = request.POST.get('action_type')
        details = request.POST.get('details')

        if action_type and details:
            action.action_type = action_type
            action.details = details
            action.updated_by = request.user
            action.save()
            messages.success(request, f"Action '{action.get_action_type_display()}' updated successfully.")
        else:
            messages.error(request, "Invalid data. Please provide action type and details.")

    return redirect('tickets:ticket_detail', pk=action.ticket.pk)

@login_required
def delete_ticket_action(request, action_id):
    action = get_object_or_404(TicketAction, id=action_id, ticket__agency=request.user.agency)
    
    # Check if the user is an admin
    if request.user.user_type != 'admin':
        messages.error(request, "You don't have permission to delete actions.")
        return redirect('tickets:ticket_detail', pk=action.ticket.pk)
    
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation')
        if confirmation == str(action_id):
            action_type = action.get_action_type_display()
            action.delete()
            messages.success(request, f"Action '{action_type}' has been successfully deleted.")
        else:
            messages.error(request, "Incorrect action ID. Deletion cancelled.")
    
    return redirect('tickets:ticket_detail', pk=action.ticket.pk)

@login_required
def view_email_in_browser(request, email_type, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    additional_context = {}

    if email_type == 'created':
        # No additional context required
        pass

    elif email_type == 'updated':
        # Retrieve the latest update action
        latest_action = ticket.actions.filter(action_type='update').order_by('-created_at').first()
        if latest_action:
            additional_context['update_message'] = latest_action.details
        else:
            additional_context['update_message'] = 'No update details available.'

    elif email_type == 'action_added':
        # Retrieve the latest action added
        action = ticket.actions.filter(action_type='action_taken').order_by('-created_at').first()
        if action:
            additional_context['action'] = action
        else:
            messages.error(request, "No action available for this ticket.")
            return redirect('tickets:ticket_detail', pk=ticket_id)
    else:
        messages.error(request, "Invalid email type.")
        return redirect('tickets:ticket_detail', pk=ticket_id)

    return send_ticket_email(request, ticket, email_type, additional_context=additional_context, preview=True)