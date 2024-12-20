#activity_log/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Meeting, Call, Email
from .forms import MeetingForm, CallForm, EmailForm
from crm.models import Company, Contact
from django.contrib.auth import get_user_model


User = get_user_model()

@login_required
def log_meeting(request, pk):
    """
    Logs a meeting for a specific company. 
    If the request method is POST, it processes the submitted form data, 
    validates the input, and saves the meeting along with associated contacts and users.
    If the request method is GET, it initializes a blank form for logging a meeting.
    """
    company = get_object_or_404(Company, pk=pk)

    if request.method == 'POST':
        form = MeetingForm(request.POST, company=company, creator=request.user)  
        if form.is_valid():
            contacts_input = form.cleaned_data.get('contacts_input', '')
            contact_ids = contacts_input.split(',') if contacts_input else []

            contacts = []
            users = []

            for contact_id in contact_ids:
                if 'contact_contact_' in contact_id:
                    contact_pk = contact_id.replace('contact_contact_', '')
                    try:
                        contact = Contact.objects.get(pk=contact_pk)
                        contacts.append(contact)
                    except Contact.DoesNotExist:
                        form.add_error(None, f"Contact with ID {contact_pk} not found.")
                elif 'contact_user_' in contact_id:
                    user_pk = contact_id.replace('contact_user_', '')
                    try:
                        user = User.objects.get(pk=user_pk)
                        users.append(user)
                    except User.DoesNotExist:
                        form.add_error(None, f"User with ID {user_pk} not found.")

            if not form.errors:
                try:
                    meeting = form.save(commit=False)
                    meeting.save()
                    meeting.contacts.add(*contacts)
                    meeting.users.add(*users)

                    messages.success(request, "Meeting logged successfully!")
                    return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity')
                except Exception as e:
                    form.add_error(None, f"An unexpected error occurred: {str(e)}")
            else:
                print("Form errors found:", form.errors)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MeetingForm(company=company, creator=request.user)  

    return render(request, 'activity_log/log_meeting.html', {'form': form, 'company': company})


@login_required
def search_attendees(request):
    """
    Searches for attendees (contacts and users) based on a query string.
    If a company primary key is provided, it retrieves contacts associated with that company
    and users associated with the user's agency. The results are limited to the first 10 matches
    for both contacts and users.
    """
    query = request.GET.get('q', '')
    company_pk = request.GET.get('company_pk')

    if not company_pk:
        return JsonResponse({'results': []})

    company = get_object_or_404(Company, pk=company_pk)
    agency = request.user.agency

    # Search for company contacts
    contacts = Contact.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query),
        company=company
    )[:10]

    # Search for users in the agency
    users = User.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query),
        agency=agency
    )[:10]

    # Prepare results, contacts first, then users
    results = []

    for contact in contacts:
        results.append({
            'id': f'contact_contact_{contact.pk}',
            'name': f"{contact.first_name} {contact.last_name} (Contact)"
        })

    for user in users:
        results.append({
            'id': f'contact_user_{user.pk}',
            'name': f"{user.first_name} {user.last_name} (User)"
        })

    return JsonResponse({'results': results})


@login_required
def view_meeting(request, pk):
    """
    Retrieves and displays the details of a specific meeting, including the associated company
    and attendees (contacts and users). If the meeting does not exist, a 404 error is raised.
    """
    meeting = get_object_or_404(Meeting, pk=pk)
    company = meeting.company

    attendees = list(meeting.contacts.all()) + list(meeting.users.all())

    context = {
        'meeting': meeting,
        'company': company,
        'attendees': attendees
    }
    return render(request, 'activity_log/view_meeting.html', context)


@login_required
def delete_meeting(request, pk):
    """
    Deletes a specific meeting if the user has the necessary permissions.
    If the user is not an admin within the agency, an error message is displayed.
    If the request method is POST, the meeting is deleted and the user is redirected.
    If the request method is GET, a confirmation page is rendered.
    """
    meeting = get_object_or_404(Meeting, pk=pk)
    company = meeting.company  # Ensure Meeting has a ForeignKey to Company

    # Check if the user is an admin within the agency
    current_user = request.user
    is_admin = User.objects.filter(
        id=current_user.id,
        user_type='admin',
        agency=company.agency  # Ensure Company has a ForeignKey to Agency
    ).exists()

    if not is_admin:
        messages.error(request, "You do not have permission to delete this meeting.")
        return redirect('activity_log:view_meeting', pk=pk)

    if request.method == 'POST':
        try:
            meeting.delete()
            messages.success(request, "Meeting deleted successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while deleting the meeting: {str(e)}")
            return redirect('activity_log:view_meeting', pk=pk)

        # Redirect to activity tab
        return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity')

    # Render confirmation page for GET request
    context = {
        'activity': meeting,
        'company': company,
        'activity_type': 'meeting', 
    }
    return render(request, 'activity_log/confirm_delete_activity.html', context)


@login_required
def log_call(request, pk):
    """
    Logs a call for a specific company. 
    If the request method is POST, it processes the submitted form data, 
    validates the input, and saves the call along with associated contacts and users.
    If the request method is GET, it initializes a blank form for logging a call.
    """
    company = get_object_or_404(Company, pk=pk)

    if request.method == 'POST':
        form = CallForm(request.POST, company=company, creator=request.user)
        
        if form.is_valid():
            contacts_input = form.cleaned_data.get('contacts_input')
            contact_ids = contacts_input.split(',') if contacts_input else []

            # Initialize lists to hold Contact and User objects
            contacts = []
            users = []

            # Loop through the contact_ids to determine if they are Contacts or Users
            for contact_id in contact_ids:
                if 'contact_contact_' in contact_id:
                    contact_pk = contact_id.replace('contact_contact_', '')
                    try:
                        contact = Contact.objects.get(pk=contact_pk)
                        contacts.append(contact)
                    except Contact.DoesNotExist:
                        form.add_error(None, f"Contact with ID {contact_pk} not found.")
                elif 'contact_user_' in contact_id:
                    user_pk = contact_id.replace('contact_user_', '')
                    try:
                        user = User.objects.get(pk=user_pk)
                        users.append(user)
                    except User.DoesNotExist:
                        form.add_error(None, f"User with ID {user_pk} not found.")

            # Only proceed with saving if no errors were added
            if not form.errors:
                try:
                    call = form.save(commit=False)
                    call.save()

                    # Assuming you have Many-to-Many fields for contacts and users in your Call model
                    call.contacts.add(*contacts)
                    call.users.add(*users)

                    messages.success(request, "Call logged successfully!")
                    return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity')
                except Exception as e:
                    form.add_error(None, f"An unexpected error occurred: {str(e)}")
            else:
                print("Form errors found:", form.errors)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CallForm(company=company, creator=request.user)

    return render(request, 'activity_log/log_call.html', {'form': form, 'company': company})


@login_required
def view_call(request, pk):
    """
    Retrieves and displays the details of a specific call, including the associated company
    and contacts. If the call does not exist, a 404 error is raised.
    """
    call = get_object_or_404(Call, pk=pk)
    company = call.company

    context = {
        'call': call,
        'company': company,
        'contacts': call.contacts.all()
    }
    return render(request, 'activity_log/view_call.html', context)


@login_required
def delete_call(request, pk):
    """
    Deletes a specific call if the user has the necessary permissions.
    If the user is not an admin within the agency, an error message is displayed.
    If the request method is POST, the call is deleted and the user is redirected.
    If the request method is GET, a confirmation page is rendered.
    """
    call = get_object_or_404(Call, pk=pk)
    company = call.company

    # Check if the user is an admin within the agency
    current_user = request.user
    is_admin = User.objects.filter(
        id=current_user.id,
        user_type='admin',
        agency=company.agency
    ).exists()

    if not is_admin:
        messages.error(request, "You do not have permission to delete this call.")
        return redirect('activity_log:view_call', pk=pk)

    if request.method == 'POST':
        try:
            call.delete()
            messages.success(request, "Call deleted successfully.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity')
        except Exception as e:
            messages.error(request, f"An error occurred while deleting the call: {str(e)}")
            return redirect('activity_log:view_call', pk=pk)

    # Render confirmation page for GET request
    context = {
        'activity': call,
        'company': company,
        'activity_type': 'call',
    }
    return render(request, 'activity_log/confirm_delete_activity.html', context)


@login_required
def log_email(request, pk):
    """
    Logs an email for a specific company. 
    If the request method is POST, it processes the submitted form data, 
    validates the input, and saves the email along with associated contacts and users.
    If the request method is GET, it initializes a blank form for logging an email.
    """
    company = get_object_or_404(Company, pk=pk)

    if request.method == 'POST':
        form = EmailForm(request.POST, company=company, creator=request.user)
        if form.is_valid():
            contacts_input = form.cleaned_data.get('contacts_input')
            contact_ids = contacts_input.split(',') if contacts_input else []

            # Initialize lists to hold Contact and User objects
            contacts = []
            users = []

            # Loop through the contact_ids to determine if they are Contacts or Users
            for contact_id in contact_ids:
                if 'contact_contact_' in contact_id:
                    contact_pk = contact_id.replace('contact_contact_', '')
                    try:
                        contact = Contact.objects.get(pk=contact_pk)
                        contacts.append(contact)
                    except Contact.DoesNotExist:
                        form.add_error(None, f"Contact with ID {contact_pk} not found.")
                elif 'contact_user_' in contact_id:
                    user_pk = contact_id.replace('contact_user_', '')
                    try:
                        user = User.objects.get(pk=user_pk)
                        users.append(user)
                    except User.DoesNotExist:
                        form.add_error(None, f"User with ID {user_pk} not found.")

            # Only proceed with saving if no errors were added
            if not form.errors:
                try:
                    email = form.save(commit=False)
                    email.save()

                    # Assuming you have Many-to-Many fields for contacts and users in your Email model
                    email.contacts.add(*contacts)
                    email.users.add(*users)

                    messages.success(request, "Email logged successfully!")
                    return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity')
                except Exception as e:
                    form.add_error(None, f"An unexpected error occurred: {str(e)}")
            else:
                print("Form errors found:", form.errors)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EmailForm(company=company, creator=request.user)

    return render(request, 'activity_log/log_email.html', {'form': form, 'company': company})


@login_required
def view_email(request, pk):
    """
    Retrieves and displays the details of a specific email, including the associated company
    and contacts. If the email does not exist, a 404 error is raised.
    """
    email = get_object_or_404(Email, pk=pk)
    company = email.company

    context = {
        'email': email,
        'company': company,
        'contacts': email.contacts.all()
    }
    return render(request, 'activity_log/view_email.html', context)


@login_required
def delete_email(request, pk):
    """
    Deletes a specific email if the user has the necessary permissions.
    If the user is not an admin within the agency, an error message is displayed.
    If the request method is POST, the email is deleted and the user is redirected.
    If the request method is GET, a confirmation page is rendered.
    """
    email = get_object_or_404(Email, pk=pk)
    company = email.company

    # Check if the user is an admin within the agency
    current_user = request.user
    is_admin = User.objects.filter(
        id=current_user.id,
        user_type='admin',
        agency=company.agency
    ).exists()

    if not is_admin:
        messages.error(request, "You do not have permission to delete this email.")
        return redirect('activity_log:view_email', pk=pk)

    if request.method == 'POST':
        try:
            email.delete()
            messages.success(request, "Email deleted successfully.")
            return redirect('crm:company_detail_with_tab', pk=company.pk, active_tab='activity')
        except Exception as e:
            messages.error(request, f"An error occurred while deleting the email: {str(e)}")
            return redirect('activity_log:view_email', pk=pk)

    # Render confirmation page for GET request
    context = {
        'activity': email,
        'company': company,
        'activity_type': 'email',
    }
    return render(request, 'activity_log/confirm_delete_activity.html', context)
