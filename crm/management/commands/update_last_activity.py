# crm/management/commands/update_last_activity.py

from django.core.management.base import BaseCommand
from django.db.models import Max
from crm.models import Company
from activity_log.models import Meeting, Call, Email
from tickets.models import Ticket

class Command(BaseCommand):
    """
    Command to update the last activity date for all companies.

    This command iterates through all companies and updates their
    last_activity_date based on the most recent activity from meetings,
    calls, emails, and tickets.

    Attributes:
        help (str): A description of what the command does.
    """
    help = 'Updates last_activity_date for all companies based on their most recent activity'

    def handle(self, *args, **kwargs):
        """
        Handle the command execution.

        This method fetches all companies and determines the latest activity
        date from various activity types. It updates the last_activity_date
        for each company accordingly.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        companies = Company.objects.all()
        for company in companies:
            # Get the latest date from all activity types
            latest_dates = []
            
            meeting_date = Meeting.objects.filter(company=company).aggregate(Max('date'))['date__max']
            if meeting_date:
                latest_dates.append(meeting_date)
                
            call_date = Call.objects.filter(company=company).aggregate(Max('date'))['date__max']
            if call_date:
                latest_dates.append(call_date)
                
            email_date = Email.objects.filter(company=company).aggregate(Max('date'))['date__max']
            if email_date:
                latest_dates.append(email_date)
                
            ticket_date = Ticket.objects.filter(company=company).aggregate(Max('created_at'))['created_at__max']
            if ticket_date:
                latest_dates.append(ticket_date)
            
            if latest_dates:
                company.last_activity_date = max(latest_dates)
                company.save(update_fields=['last_activity_date'])
                self.stdout.write(f"Updated {company.company_name}")