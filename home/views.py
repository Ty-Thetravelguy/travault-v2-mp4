# home/views.py

from django.views.generic import TemplateView
import logging
import time

# Initialize the logger for tracking view performance and access
logger = logging.getLogger(__name__)


class HomePageView(TemplateView):
    """
    View to render the home page.

    This view renders the main home page of the website using a template.
    It uses Django's TemplateView to serve a static HTML page without any
    complex logic or data fetching.

    Attributes:
        template_name (str): The path to the template used for rendering the home page.
    """
    template_name = 'home/index.html'

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the home page.
        
        Logs the rendering time for performance monitoring.
        """
        logger.info("Rendering the home page.")
        start_time = time.time()

        response = super().get(request, *args, **kwargs)

        logger.info(f"HomePageView completed in {time.time() - start_time:.2f} seconds.")
        return response


class TermsOfServiceView(TemplateView):
    """
    View to render the Terms of Service page.

    This view displays the Terms of Service for the website using a template.
    It provides users with information about the terms they agree to when
    using the site.

    Attributes:
        template_name (str): The path to the template used for rendering the Terms of Service page.
    """
    template_name = "terms_of_service.html"

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the Terms of Service page.
        
        Logs the rendering time for performance monitoring.
        """
        logger.info("Rendering the Terms of Service page.")
        start_time = time.time()

        response = super().get(request, *args, **kwargs)

        logger.info(f"TermsOfServiceView completed in {time.time() - start_time:.2f} seconds.")
        return response


class PrivacyPolicyView(TemplateView):
    """
    View to render the Privacy Policy page.

    This view displays the Privacy Policy of the website using a template.
    It provides users with information about how their data is collected,
    used, and protected by the site.

    Attributes:
        template_name (str): The path to the template used for rendering the Privacy Policy page.
    """
    template_name = "privacy_policy.html"

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for the Privacy Policy page.
        
        Logs the rendering time for performance monitoring.
        """
        logger.info("Rendering the Privacy Policy page.")
        start_time = time.time()

        response = super().get(request, *args, **kwargs)

        logger.info(f"PrivacyPolicyView completed in {time.time() - start_time:.2f} seconds.")
        return response