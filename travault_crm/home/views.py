# home/views.py

from django.views.generic import TemplateView

class HomePageView(TemplateView):
    template_name = 'home/index.html'

class TermsOfServiceView(TemplateView):
    template_name = "terms_of_service.html"

class PrivacyPolicyView(TemplateView):
    template_name = "privacy_policy.html"