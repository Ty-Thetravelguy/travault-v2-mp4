# activity_log/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Meeting

@shared_task
def send_follow_up_email(meeting_id):
    """
    Sends a follow-up reminder email for a meeting.
    """
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        if meeting.to_do_task_date and meeting.to_do_task_message:
            subject = f"Reminder: Follow-Up Task for Meeting '{meeting.subject}'"
            message = f"""Hello {meeting.creator.first_name},

This is a reminder for your follow-up task:

Task: {meeting.to_do_task_message}
Scheduled Date: {meeting.to_do_task_date}

Best regards,
Your Company"""
            recipient_list = [meeting.creator.email]

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
            )
            print(f"Sent follow-up email for meeting '{meeting.subject}' to {meeting.creator.email}")
    except Meeting.DoesNotExist:
        print(f"Meeting with id {meeting_id} does not exist.")
    except Exception as e:
        print(f"Error sending follow-up email for meeting id {meeting_id}: {e}")
