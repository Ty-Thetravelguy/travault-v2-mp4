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
import logging

# Initialize logger
logger = logging.getLogger(__name__)


@login_required
def view_tickets(request):
    """View function to display tickets for the logged-in user's agency.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered HTML page displaying the tickets and users.
    """
    # Log the start of the view function
    logger.info("Starting view_tickets function for user: %s", request.user.username)

    # Retrieve tickets associated with the user's agency, ordered by creation date (newest first)
    tickets = Ticket.objects.filter(agency=request.user.agency).order_by('-created_at')
    logger.debug("Retrieved %d tickets for agency: %s", tickets.count(), request.user.agency)

    # Retrieve users associated with the user's agency
    users = CustomUser.objects.filter(agency=request.user.agency)
    logger.debug("Retrieved %d users for agency: %s", users.count(), request.user.agency)

    # Render the view_tickets.html template with the tickets and users context
    response = render(request, 'tickets/view_tickets.html', {'tickets': tickets, 'users': users})
    
    # Log the completion of the view function
    logger.info("Completed view_tickets function for user: %s", request.user.username)
    
    return response

class TicketSubjectAutocomplete(autocomplete.Select2QuerySetView):
    """Autocomplete view for ticket subjects.

    This view provides a queryset of ticket subjects based on user input.

    Attributes:
        request: The HTTP request object.
    """
    
    def get_queryset(self):
        """Return a queryset of ticket subjects based on the user's input.

        Returns:
            QuerySet: A filtered queryset of TicketSubject objects.
        """
        # Log the start of the get_queryset method
        logger.info("Starting get_queryset for TicketSubjectAutocomplete")

        # If the user is not authenticated, return an empty queryset
        if not self.request.user.is_authenticated:
            logger.warning("Unauthenticated access attempt to TicketSubjectAutocomplete")
            return TicketSubject.objects.none()

        # Retrieve all ticket subjects
        qs = TicketSubject.objects.all()

        # Filter the queryset based on the user's input (if provided)
        if self.q:
            qs = qs.filter(subject__icontains=self.q)
            logger.debug("Filtered queryset based on input: %s", self.q)

        # Log the completion of the get_queryset method
        logger.info("Completed get_queryset for TicketSubjectAutocomplete")
        
        # Return the filtered queryset
        return qs

# Create an instance of the TicketSubjectAutocomplete view
ticket_subject_autocomplete = TicketSubjectAutocomplete.as_view()


@login_required
def manage_subjects(request):
    """View function to manage ticket subjects for the logged-in user's agency.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered HTML page displaying the ticket subjects and their counts.
    """
    # Log the start of the manage_subjects function
    logger.info("Starting manage_subjects function for user: %s", request.user.username)

    # Retrieve subjects associated with the user's agency and annotate with ticket count
    subjects = TicketSubject.objects.filter(
        agency=request.user.agency
    ).annotate(
        ticket_count=Count('ticket')
    ).order_by(Lower('subject'))
    logger.debug("Retrieved %d subjects for agency: %s", subjects.count(), request.user.agency)
    
    # Render the manage_subjects.html template with the subjects context
    response = render(request, 'tickets/manage_subjects.html', {'subjects': subjects})
    
    # Log the completion of the manage_subjects function
    logger.info("Completed manage_subjects function for user: %s", request.user.username)
    
    return response


@login_required
def ticket_subject_autocomplete(request):
    """View function to provide autocomplete suggestions for ticket subjects.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse containing a list of ticket subjects matching the query.
    """
    # Log the start of the autocomplete function
    logger.info("Starting ticket_subject_autocomplete for user: %s", request.user.username)

    # Get the query parameter for subject filtering
    query = request.GET.get('q', '')
    logger.debug("Autocomplete query: %s", query)
    
    # Retrieve ticket subjects that match the query, limiting to 10 results
    subjects = TicketSubject.objects.filter(subject__icontains=query)[:10]
    logger.debug("Found %d subjects matching query", len(subjects))
    
    # Prepare the data for the JSON response
    data = [{'id': subject.id, 'text': subject.subject} for subject in subjects]
    
    # Log the completion of the autocomplete function
    logger.info("Completed ticket_subject_autocomplete for user: %s", request.user.username)

    # Return the data as a JSON response
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def create_ticket_subject(request):
    """View function to create a new ticket subject.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse indicating the result of the creation attempt.
    """
    # Log the start of the create_ticket_subject function
    logger.info("Starting create_ticket_subject for user: %s", request.user.username)

    # Get the subject from the POST request
    subject = request.POST.get('subject')
    logger.debug("Subject to create: %s", subject)
    
    if subject:
        # Create or get the ticket subject
        new_subject, created = TicketSubject.objects.get_or_create(
            subject=subject,
            agency=request.user.agency
        )
        
        # Provide feedback based on whether the subject was created or already exists
        if created:
            messages.success(request, f"New ticket subject '{subject}' has been created.")
            logger.info("Created new ticket subject: %s", subject)
        else:
            messages.info(request, f"Ticket subject '{subject}' already exists.")
            logger.info("Ticket subject already exists: %s", subject)
        
        # Return the new subject details as a JSON response
        return JsonResponse({
            'id': new_subject.id, 
            'subject': new_subject.subject,
            'created': created,
            'redirect': reverse('tickets:manage_subjects')
        })
    else:
        # Handle the case where no subject was provided
        messages.error(request, "No subject provided. Please enter a subject.")
        logger.warning("No subject provided in create_ticket_subject")
        return JsonResponse({'error': 'No subject provided'}, status=400)


@login_required
@require_POST
def update_subject(request, subject_id):
    """View function to update an existing ticket subject.

    Args:
        request: The HTTP request object.
        subject_id: The ID of the subject to be updated.

    Returns:
        JsonResponse indicating the result of the update attempt.
    """
    # Log the start of the update_subject function
    logger.info("Starting update_subject for subject ID: %d by user: %s", subject_id, request.user.username)

    try:
        # Retrieve the ticket subject by ID
        subject = TicketSubject.objects.get(id=subject_id)
        
        # Get the new subject name from the POST request
        new_subject_name = request.POST.get('subject')
        logger.debug("New subject name: %s", new_subject_name)
        
        if new_subject_name:
            # Update the subject name and save the changes
            subject.subject = new_subject_name
            subject.save()
            messages.success(request, f"Subject updated successfully to '{new_subject_name}'.")
            logger.info("Subject ID %d updated to: %s", subject_id, new_subject_name)
            return JsonResponse({'success': True})
        else:
            # Handle the case where no new subject name was provided
            messages.error(request, "No subject name provided.")
            logger.warning("No new subject name provided for subject ID: %d", subject_id)
            return JsonResponse({'success': False, 'error': 'No subject name provided'}, status=400)
    
    except TicketSubject.DoesNotExist:
        # Handle the case where the subject does not exist
        messages.error(request, "Subject not found.")
        logger.error("Subject ID %d not found", subject_id)
        return JsonResponse({'success': False, 'error': 'Subject not found'}, status=404)


@login_required
@require_POST
def delete_subject(request, subject_id):
    """View function to delete a ticket subject.

    Args:
        request: The HTTP request object.
        subject_id: The ID of the subject to be deleted.

    Returns:
        JsonResponse indicating the result of the deletion attempt.
    """
    # Log the start of the delete_subject function
    logger.info("Starting delete_subject for subject ID: %d by user: %s", subject_id, request.user.username)

    try:
        subject = TicketSubject.objects.get(id=subject_id)
        
        # Check if there are any tickets associated with this subject
        if Ticket.objects.filter(subject=subject).exists():
            logger.warning("Attempt to delete subject with associated tickets: %d", subject_id)
            return JsonResponse({
                'success': False, 
                'error': 'Cannot delete this subject as it has tickets associated with it.'
            }, status=400)
        
        subject_name = subject.subject
        subject.delete()
        messages.success(request, f"Subject '{subject_name}' has been deleted.")
        logger.info("Subject ID %d deleted successfully", subject_id)
        return JsonResponse({'success': True})
    except TicketSubject.DoesNotExist:
        messages.error(request, "Subject not found.")
        logger.error("Subject ID %d not found", subject_id)
        return JsonResponse({'success': False, 'error': 'Subject not found'}, status=404)
    except ProtectedError:
        messages.error(request, "Cannot delete this subject as it is referenced by other parts of the system.")
        logger.error("ProtectedError: Subject ID %d is referenced by other parts of the system", subject_id)
        return JsonResponse({
            'success': False, 
            'error': 'Cannot delete this subject as it is referenced by other parts of the system.'
        }, status=400)


@login_required
def open_ticket(request, company_id=None):
    """View function to open a new ticket.

    Args:
        request: The HTTP request object.
        company_id: Optional; The ID of the company for which the ticket is being opened.

    Returns:
        Rendered HTML page for ticket creation or redirects to ticket detail on success.
    """
    # Log the start of the open_ticket function
    logger.info("Starting open_ticket for user: %s", request.user.username)

    if company_id:
        company = get_object_or_404(Company, id=company_id)
        initial_data = {'company': company.id}
    else:
        company = None
        initial_data = {}

    if request.method == 'POST':
        form = TicketForm(data=request.POST, agency=request.user.agency)
        if 'company' in request.POST and not form.is_valid():
            # If only company was changed, re-render the form
            company = form.cleaned_data.get('company') or company
            return render(request, 'tickets/open_ticket.html', {'form': form, 'company': company})
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.company = form.cleaned_data['company']  # Get company from form
            ticket.owner = request.user
            ticket.agency = request.user.agency
            ticket.save()

            messages.success(request, f"Ticket #{ticket.id} has been successfully created.")
            logger.info("Ticket #%d created successfully by user: %s", ticket.id, request.user.username)
            send_ticket_email(request, ticket, 'created')
            return redirect('tickets:ticket_detail', pk=ticket.id)
        else:
            messages.error(request, "There was an error creating the ticket. Please check the form and try again.")
            logger.warning("Ticket creation failed for user: %s", request.user.username)
    else:
        form = TicketForm(initial={'company': company}, agency=request.user.agency)

    return render(request, 'tickets/open_ticket.html', {'form': form, 'company': company})


def ticket_list(request):
    """View function to list tickets for the logged-in user's agency.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered HTML page displaying the list of tickets.
    """
    # Log the start of the ticket_list function
    logger.info("Starting ticket_list for user: %s", request.user.username)

    # Filter tickets based on the agency of the logged-in user
    tickets = Ticket.objects.filter(agency=request.user.agency)
    logger.debug("Retrieved %d tickets for agency: %s", tickets.count(), request.user.agency)

    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})


def preview_ticket_email(request, ticket_id):
    """View function to preview the ticket creation email.

    Args:
        request: The HTTP request object.
        ticket_id: The ID of the ticket for which the email is being previewed.

    Returns:
        Rendered HTML page displaying the email preview.
    """
    # Log the start of the preview_ticket_email function
    logger.info("Starting preview_ticket_email for ticket ID: %d", ticket_id)

    ticket = Ticket.objects.get(pk=ticket_id)
    ticket_url = request.build_absolute_uri(reverse('tickets:ticket_detail', args=[ticket.pk]))
    
    context = {
        'ticket': ticket,
        'ticket_url': ticket_url,
    }
    
    return render(request, 'tickets/email/ticket_created_email.html', context)


@login_required
def delete_ticket_confirm(request, pk):
    """View function to confirm and delete a ticket.

    Args:
        request: The HTTP request object.
        pk: The primary key of the ticket to be deleted.

    Returns:
        Rendered HTML page for confirmation or redirects after deletion.
    """
    # Log the start of the delete_ticket_confirm function
    logger.info("Starting delete_ticket_confirm for ticket ID: %d by user: %s", pk, request.user.username)

    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)
    
    # Check if the user is an admin
    if request.user.user_type != 'admin':
        messages.error(request, "You don't have permission to delete tickets.")
        logger.warning("Unauthorized delete attempt by user: %s for ticket ID: %d", request.user.username, pk)
        return redirect('tickets:ticket_detail', pk=ticket.pk)
    
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation')
        if confirmation == str(ticket.pk):
            ticket_number = ticket.pk 
            ticket.delete()
            messages.success(request, f"Ticket #{ticket_number} has been successfully deleted.")
            logger.info("Ticket #%d deleted successfully by user: %s", ticket_number, request.user.username)
            return redirect('tickets:view_tickets')
        else:
            messages.error(request, "Incorrect ticket number. Deletion cancelled.")
            logger.warning("Deletion cancelled due to incorrect ticket number for ticket ID: %d", pk)
    
    return render(request, 'tickets/delete_ticket_confirm.html', {'ticket': ticket})


@login_required
@require_POST
def update_ticket_field(request, pk):
    """View to update a specific field of a ticket via AJAX.

    Args:
        request: The HTTP request object.
        pk: The primary key of the ticket to be updated.

    Returns:
        JsonResponse indicating the result of the update attempt.
    """
    # Log the start of the update_ticket_field function
    logger.info("Starting update_ticket_field for ticket ID: %d by user: %s", pk, request.user.username)

    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)
    field = request.POST.get('field')
    value = request.POST.get('value')

    valid_fields = ['owner', 'assigned_to', 'priority', 'status']

    # Restrict editing if the ticket is closed and the user is not an admin
    if ticket.status == 'closed' and request.user.user_type != 'admin':
        messages.error(request, 'This ticket is closed and cannot be edited.')
        logger.warning("Unauthorized edit attempt on closed ticket ID: %d by user: %s", pk, request.user.username)
        return redirect('ticket_detail', pk=ticket.pk)

    if field not in valid_fields:
        logger.error("Invalid field update attempt: %s for ticket ID: %d", field, pk)
        return JsonResponse({'success': False, 'error': 'Invalid field'}, status=400)

    try:
        old_value = getattr(ticket, field)
        field_object = Ticket._meta.get_field(field)

        if field in ['owner', 'assigned_to']:
            user = get_object_or_404(CustomUser, pk=value, agency=request.user.agency)
            setattr(ticket, field, user)
            # Use get_full_name or fallback to username
            new_display = user.get_full_name()
            old_display = old_value.get_full_name() if old_value else 'None'
        else:
            setattr(ticket, field, value)
            # For choice fields, get display values if available
            if field == 'priority':
                old_display = dict(ticket.PRIORITY_CHOICES).get(old_value, old_value)
                new_display = dict(ticket.PRIORITY_CHOICES).get(value, value)
            elif field == 'status':
                old_display = dict(ticket.STATUS_CHOICES).get(old_value, old_value)
                new_display = dict(ticket.STATUS_CHOICES).get(value, value)
            else:
                old_display = old_value if old_value else 'None'
                new_display = value

        ticket.updated_by = request.user  # Set the user who made the update
        ticket.save()

        # Format field name for display
        field_name_formatted = field.replace('_', ' ').capitalize()

        # Create a more focused update message
        if field == 'assigned_to':
            update_message = f"Ticket assigned to {new_display}"
        elif field == 'owner':
            update_message = f"Ticket ownership transferred to {new_display}"
        else:
            update_message = f"{field_name_formatted} updated to '{new_display}'"

        additional_context = {
            'update_message': update_message,
        }

        # Trigger email notification
        email_type = 'updated'
        send_ticket_email(request, ticket, email_type, additional_context=additional_context)

        # Django messages for UI feedback
        messages.success(request, f"{field_name_formatted} updated successfully. {update_message}")
        logger.info("Ticket ID %d field '%s' updated successfully by user: %s", pk, field, request.user.username)

        return JsonResponse({
            'success': True,
            'message': 'Ticket updated successfully.',
            'reload': True  # Add this flag to indicate a reload is needed
        })
    except Exception as e:
        logger.error("Error updating ticket ID %d: %s", pk, str(e))
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def ticket_detail(request, pk):
    """View function to display the details of a specific ticket.

    Args:
        request: The HTTP request object.
        pk: The primary key of the ticket to be displayed.

    Returns:
        Rendered HTML page displaying the ticket details.
    """
    # Log the start of the ticket_detail function
    logger.info("Starting ticket_detail for ticket ID: %d by user: %s", pk, request.user.username)

    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)
    agency_users = CustomUser.objects.filter(agency=request.user.agency)
    status_choices = ['open', 'in_progress', 'closed']
    
    # Get the sort order from GET parameters, default to 'desc' (newest first)
    sort_order = request.GET.get('sort', 'desc')
    if sort_order == 'asc':
        actions = ticket.actions.all().order_by('created_at')
    else:
        actions = ticket.actions.all().order_by('-created_at')
    
    context = {
        'ticket': ticket,
        'agency_users': agency_users,
        'status_choices': status_choices,
        'actions': actions,
        'ticket_action_types': TicketAction.ACTION_TYPES,
        'sort_order': sort_order,  # Pass the sort order to the template
    }

    # Log the completion of the ticket_detail function
    logger.info("Completed ticket_detail for ticket ID: %d by user: %s", pk, request.user.username)

    return render(request, 'tickets/ticket_detail.html', context)


@login_required
def edit_ticket(request, pk):
    """View function to edit a ticket.

    Args:
        request: The HTTP request object.
        pk: The primary key of the ticket to be edited.

    Returns:
        Rendered HTML page for ticket editing or redirects after successful update.
    """
    # Log the start of the edit_ticket function
    logger.info("Starting edit_ticket for ticket ID: %d by user: %s", pk, request.user.username)

    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)

    # Restrict editing if the ticket is closed unless the user is an admin
    if ticket.status == 'closed' and request.user.user_type != 'admin':
        messages.error(request, 'This ticket is closed and cannot be edited.')
        logger.warning("Unauthorized edit attempt on closed ticket ID: %d by user: %s", pk, request.user.username)
        return redirect('ticket_detail', pk=ticket.pk)
    
    if request.method == 'POST':
        form = TicketForm(data=request.POST, instance=ticket, agency=request.user.agency)

        # Prevent editing of specific fields if the ticket is closed
        if ticket.status == 'closed':
            for field in ['priority', 'status', 'owner', 'assigned']:
                if field in form.fields:
                    form.fields[field].disabled = True

        if form.is_valid():
            updated_ticket = form.save(commit=False)
            updated_ticket.updated_by = request.user
            updated_ticket.save()
            messages.success(request, 'Ticket updated successfully.')
            logger.info("Ticket ID %d updated successfully by user: %s", pk, request.user.username)
            return redirect('tickets:ticket_detail', pk=updated_ticket.pk)
        else:
            messages.error(request, "There was an error updating the ticket. Please check the form and try again.")
            logger.warning("Ticket update failed for ticket ID: %d by user: %s", pk, request.user.username)
    else:
        form = TicketForm(instance=ticket, agency=request.user.agency)

        # Make specific fields read-only if the ticket is closed
        if ticket.status == 'closed':
            for field in ['priority', 'status', 'owner', 'assigned']:
                if field in form.fields:
                    form.fields[field].disabled = True

    context = {
        'form': form,
        'ticket': ticket,
    }
    return render(request, 'tickets/edit_ticket.html', context)


@require_POST
@login_required
def add_ticket_action(request, pk):
    """View function to add an action to a ticket.

    Args:
        request: The HTTP request object.
        pk: The primary key of the ticket to which the action is being added.

    Returns:
        Redirects to the ticket detail page.
    """
    # Log the start of the add_ticket_action function
    logger.info("Starting add_ticket_action for ticket ID: %d by user: %s", pk, request.user.username)

    ticket = get_object_or_404(Ticket, pk=pk, agency=request.user.agency)

    # Prevent adding actions if the ticket is closed
    if ticket.status == 'closed' and request.user.user_type != 'admin':
        messages.error(request, "Actions cannot be added to a closed ticket.")
        logger.warning("Unauthorized action addition attempt on closed ticket ID: %d by user: %s", pk, request.user.username)
        return redirect('tickets:ticket_detail', pk=pk)

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
        logger.info("Action added to ticket ID: %d by user: %s", pk, request.user.username)

        # Ensure the ticket has an assigned user (assigned_to)
        if not ticket.assigned_to:
            ticket.assigned_to = request.user
            ticket.save()

        # Send action added email
        additional_context = {
            'action': action,
            'email_type': 'action_added'
        }
        send_ticket_email(request, ticket, 'action_added', additional_context)
    else:
        messages.error(request, "Invalid data. Please provide action type and details.")
        logger.warning("Invalid data for action addition on ticket ID: %d by user: %s", pk, request.user.username)

    return redirect('tickets:ticket_detail', pk=pk)


@login_required
def edit_ticket_action(request, action_id):
    """View function to edit an action on a ticket.

    Args:
        request: The HTTP request object.
        action_id: The ID of the action to be edited.

    Returns:
        Redirects to the ticket detail page.
    """
    # Log the start of the edit_ticket_action function
    logger.info("Starting edit_ticket_action for action ID: %d by user: %s", action_id, request.user.username)

    action = get_object_or_404(TicketAction, id=action_id, ticket__agency=request.user.agency)

    # Prevent editing actions if the ticket is closed
    if action.ticket.status == 'closed' and request.user.user_type != 'admin':
        messages.error(request, "Actions on closed tickets cannot be edited.")
        logger.warning("Unauthorized action edit attempt on closed ticket ID: %d by user: %s", action.ticket.pk, request.user.username)
        return redirect('tickets:ticket_detail', pk=action.ticket.pk)

    if request.method == 'POST':
        action_type = request.POST.get('action_type')
        details = request.POST.get('details')

        if action_type and details:
            action.action_type = action_type
            action.details = details
            action.updated_by = request.user
            action.save()
            messages.success(request, f"Action '{action.get_action_type_display()}' updated successfully.")
            logger.info("Action ID %d updated successfully by user: %s", action_id, request.user.username)
        else:
            messages.error(request, "Invalid data. Please provide action type and details.")
            logger.warning("Invalid data for action update on action ID: %d by user: %s", action_id, request.user.username)

    return redirect('tickets:ticket_detail', pk=action.ticket.pk)


@login_required
def delete_ticket_action(request, action_id):
    """View function to delete an action from a ticket.

    Args:
        request: The HTTP request object.
        action_id: The ID of the action to be deleted.

    Returns:
        Redirects to the ticket detail page.
    """
    # Log the start of the delete_ticket_action function
    logger.info("Starting delete_ticket_action for action ID: %d by user: %s", action_id, request.user.username)

    action = get_object_or_404(TicketAction, id=action_id, ticket__agency=request.user.agency)
    
    # Check if the user is an admin
    if request.user.user_type != 'admin':
        messages.error(request, "You don't have permission to delete actions.")
        logger.warning("Unauthorized delete attempt by user: %s for action ID: %d", request.user.username, action_id)
        return redirect('tickets:ticket_detail', pk=action.ticket.pk)
    
    if request.method == 'POST':
        confirmation = request.POST.get('confirmation')
        if confirmation == str(action_id):
            action_type = action.get_action_type_display()
            action.delete()
            messages.success(request, f"Action '{action_type}' has been successfully deleted.")
            logger.info("Action ID %d deleted successfully by user: %s", action_id, request.user.username)
        else:
            messages.error(request, "Incorrect action ID. Deletion cancelled.")
            logger.warning("Deletion cancelled due to incorrect action ID for action ID: %d", action_id)
    
    return redirect('tickets:ticket_detail', pk=action.ticket.pk)


@login_required
def view_email_in_browser(request, email_type, ticket_id):
    """View function to preview an email related to a ticket.

    Args:
        request: The HTTP request object.
        email_type: The type of email to preview.
        ticket_id: The ID of the ticket related to the email.

    Returns:
        Rendered HTML page displaying the email preview.
    """
    # Log the start of the view_email_in_browser function
    logger.info("Starting view_email_in_browser for ticket ID: %d and email type: %s", ticket_id, email_type)

    # Ensure user has access to this ticket
    ticket = get_object_or_404(Ticket, pk=ticket_id, agency=request.user.agency)
    
    # Validate email type
    valid_email_types = ['created', 'updated', 'action_added']
    if email_type not in valid_email_types:
        messages.error(request, "Invalid email type.")
        logger.error("Invalid email type: %s for ticket ID: %d", email_type, ticket_id)
        return redirect('tickets:ticket_detail', pk=ticket_id)

    additional_context = {
        'email_type': email_type,
        'is_preview': True
    }

    if email_type == 'created':
        # For created emails, we just need the ticket details which are already available
        pass

    elif email_type == 'updated':
        # For updated emails, get the latest update action
        latest_update = ticket.actions.filter(
            action_type='update',
            is_system_generated=True
        ).order_by('-created_at').first()
        
        if latest_update:
            additional_context['update_message'] = latest_update.details
        else:
            additional_context['update_message'] = 'No update details available.'

    elif email_type == 'action_added':
        # For action added emails, get the latest non-system-generated action
        latest_action = ticket.actions.filter(
            is_system_generated=False
        ).order_by('-created_at').first()
        
        if latest_action:
            additional_context['action'] = latest_action
        else:
            messages.error(request, "No action available for this ticket.")
            logger.warning("No action available for ticket ID: %d", ticket_id)
            return redirect('tickets:ticket_detail', pk=ticket_id)

    # Generate the email preview
    return send_ticket_email(
        request=request,
        ticket=ticket,
        email_type=email_type,
        additional_context=additional_context,
        preview=True
    )


@login_required
def reopen_ticket(request, pk):
    """View function to reopen a closed ticket.

    Args:
        request: The HTTP request object.
        pk: The primary key of the ticket to be reopened.

    Returns:
        Redirects to the manage closed tickets page.
    """
    # Log the start of the reopen_ticket function
    logger.info("Starting reopen_ticket for ticket ID: %d by user: %s", pk, request.user.username)

    ticket = get_object_or_404(Ticket, pk=pk)

    # Only allow admins to reopen closed tickets
    if request.user.user_type == 'admin':
        if ticket.status == 'closed':
            ticket.status = 'open'
            ticket.admin_override_save()
            messages.success(request, 'Ticket reopened successfully.')
            logger.info("Ticket ID %d reopened successfully by user: %s", pk, request.user.username)
        else:
            messages.error(request, 'Ticket is not closed, so it cannot be reopened.')
            logger.warning("Attempt to reopen non-closed ticket ID: %d by user: %s", pk, request.user.username)
    else:
        messages.error(request, 'You do not have permission to reopen this ticket.')
        logger.warning("Unauthorized reopen attempt by user: %s for ticket ID: %d", request.user.username, pk)

    return redirect('tickets:manage_closed_tickets')


@login_required
def manage_closed_tickets(request):
    """View function to manage closed tickets.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered HTML page displaying the list of closed tickets.
    """
    # Log the start of the manage_closed_tickets function
    logger.info("Starting manage_closed_tickets for user: %s", request.user.username)

    if request.user.user_type != 'admin':
        messages.error(request, "You do not have permission to access this page.")
        logger.warning("Unauthorized access attempt to manage_closed_tickets by user: %s", request.user.username)
        return redirect('tickets:view_tickets')

    closed_tickets = Ticket.objects.filter(status='closed', agency=request.user.agency)
    logger.debug("Retrieved %d closed tickets for agency: %s", closed_tickets.count(), request.user.agency)

    return render(request, 'tickets/manage_closed_tickets.html', {'closed_tickets': closed_tickets})
