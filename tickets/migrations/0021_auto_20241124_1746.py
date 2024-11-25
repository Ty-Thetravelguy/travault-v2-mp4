from django.db import migrations

def populate_agency(apps, schema_editor):
    TicketSubject = apps.get_model('tickets', 'TicketSubject')
    Ticket = apps.get_model('tickets', 'Ticket')
    
    # For each subject, find a ticket that uses it and get the agency from that ticket
    for subject in TicketSubject.objects.all():
        ticket = Ticket.objects.filter(subject=subject).first()
        if ticket:
            subject.agency = ticket.agency
            subject.save()
        else:
            # If no ticket exists for this subject, you might want to:
            # Option 1: Delete the subject
            subject.delete()
            # OR Option 2: Assign it to a default agency (you'll need to know the ID)
            # subject.agency_id = 1  # Replace 1 with your default agency ID
            # subject.save()

class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0020_ticketsubject_agency_alter_ticketsubject_subject_and_more'),  # Replace with the previous migration name
    ]

    operations = [
        migrations.RunPython(populate_agency),
    ]