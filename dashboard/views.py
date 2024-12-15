#dashboard/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard_view(request):
    """
    View to display the user dashboard.

    This view renders the dashboard for the logged-in user. It is a simple view
    meant to display dashboard content, which can include various widgets, summaries,
    or analytics relevant to the user's activity or data.

    Args:
        request (HttpRequest): The incoming HTTP request from the client.

    Returns:
        HttpResponse: Renders the dashboard/index.html template.
    """
    # Render the dashboard template
    return render(request, 'dashboard/index.html')