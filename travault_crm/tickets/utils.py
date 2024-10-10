from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse


def send_ticket_email(request, ticket, email_type, additional_context=None, preview=False):
    email_templates = {
        'created': 'tickets/email/ticket_created_email.html',
        'updated': 'tickets/email/ticket_updated_email.html',
        'action_added': 'tickets/email/ticket_action_added_email.html',
    }
    
    subject = f'Ticket {email_type.capitalize()}: #{ticket.pk}'
    ticket_url = request.build_absolute_uri(reverse('tickets:ticket_detail', args=[ticket.pk]))
    view_in_browser_url = request.build_absolute_uri(reverse('tickets:view_email_in_browser', args=[email_type, ticket.pk]))
    
    context = {
        'ticket': ticket,
        'ticket_url': ticket_url,
        'view_in_browser_url': view_in_browser_url,
    }
    
    if additional_context:
        context.update(additional_context)
    
    html_message = render_to_string(email_templates[email_type], context)
    
    # If preview is requested, return the HTML content
    if preview:
        return HttpResponse(html_message)
    
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    
    to_email = ticket.owner.email if ticket.owner else None

    if to_email:
        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)