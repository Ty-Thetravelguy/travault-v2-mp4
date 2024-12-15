from django import template
from django.forms import CheckboxInput, RadioSelect

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    """
    Adds a CSS class to a Django form field widget, unless the widget is a CheckboxInput or RadioSelect.

    Args:
        value: The form field or widget to which the CSS class should be added.
        css_class: The CSS class to add to the widget.

    Returns:
        The form field with the added CSS class, or the original value if it is not a form field or is a CheckboxInput/RadioSelect.
    """
    # Check if 'value' is a form field (has 'as_widget' method)
    if hasattr(value, 'field') and hasattr(value.field, 'widget'):
        if isinstance(value.field.widget, (CheckboxInput, RadioSelect)):
            return value
        return value.as_widget(attrs={"class": css_class})
    # If 'value' is not a form field, return it as is
    return value