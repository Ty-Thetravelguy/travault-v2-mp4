from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse


def send_ticket_email(request, ticket, email_type, additional_context=None, preview=False):
    """Send an email regarding a ticket.

    Args:
        request: The HTTP request object.
        ticket: The ticket object to which the email relates.
        email_type: The type of email to send (created, updated, action_added).
        additional_context: Any additional context to include in the email.
        preview: If True, return the HTML content instead of sending an email.
    """
    
    # Define email templates based on the email type
    email_templates = {
        'created': 'tickets/email/ticket_created_email.html',
        'updated': 'tickets/email/ticket_updated_email.html',
        'action_added': 'tickets/email/ticket_action_added_email.html',
    }

    # Prepare the email subject using the ticket's primary key
    subject = f'Ticket {email_type.capitalize()}: #{ticket.pk}'

    # Build URLs for the ticket and viewing the email in the browser
    ticket_url = request.build_absolute_uri(reverse('tickets:ticket_detail', args=[ticket.pk]))
    view_in_browser_url = request.build_absolute_uri(reverse('tickets:view_email_in_browser', args=[email_type, ticket.pk]))
    
    context = {
        'ticket': ticket,
        'ticket_url': ticket_url,
        'view_in_browser_url': view_in_browser_url,
    }
    
    # Add any additional context provided
    if additional_context:
        context.update(additional_context)
    
    # Render the email template with the context
    html_message = render_to_string(email_templates[email_type], context)
    
    # If preview is requested, return the HTML content
    if preview:
        return HttpResponse(html_message)
    
    # Prepare the plain text version of the email
    plain_message = strip_tags(html_message)
    
    # Set the default from email address
    from_email = settings.DEFAULT_FROM_EMAIL
    
    # Determine the email address to send the email to
    to_email = ticket.assigned_to.email if ticket.assigned_to else (ticket.owner.email if ticket.owner else None)

    # If an email address is found, send the email
    if to_email:
        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)