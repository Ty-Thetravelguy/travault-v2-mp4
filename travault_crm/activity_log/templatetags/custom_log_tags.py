from django import template
from django.forms import CheckboxInput, RadioSelect

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    # Check if 'value' is a form field (has 'as_widget' method)
    if hasattr(value, 'field') and hasattr(value.field, 'widget'):
        if isinstance(value.field.widget, (CheckboxInput, RadioSelect)):
            return value
        return value.as_widget(attrs={"class": css_class})
    # If 'value' is not a form field, return it as is
    return value

