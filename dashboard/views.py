#dashboard/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import logging
import time

# Initialize the logger
logger = logging.getLogger(__name__)

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
    logger.info("Entering dashboard_view.")
    start_time = time.time()

    # Placeholder for any dashboard-specific logic
    # Add any logic needed to fetch and prepare data for the dashboard
    logger.debug("Preparing data for the dashboard.")

    # Render the dashboard template
    response = render(request, 'dashboard/index.html')

    logger.info(f"dashboard_view completed in {time.time() - start_time:.2f} seconds.")
    return response
