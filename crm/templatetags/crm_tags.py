# crm/templatetags/crm_tags.py

from django import template
from django.forms import CheckboxInput, RadioSelect
from django.utils.safestring import SafeString
from activity_log.models import Meeting, Call, Email
from tickets.models import Ticket

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    """
    Add a CSS class to a form field widget.

    This filter adds a specified CSS class to the widget of a form field,
    preserving any existing classes.

    Args:
        value: The form field to which the class will be added.
        css_class (str): The CSS class to add.

    Returns:
        SafeString: The modified form field widget with the new class.
    """
    if isinstance(value, SafeString):
        return value
    if isinstance(value.field.widget, (CheckboxInput, RadioSelect)):
        return value
    existing_classes = value.field.widget.attrs.get('class', '')
    new_classes = f"{existing_classes} {css_class}".strip()
    return value.as_widget(attrs={"class": new_classes})


@register.filter(name='attr')
def set_attr(field, attr_name_value):
    """
    Set an attribute on a form field widget.

    This filter sets a specified attribute on the widget of a form field.

    Args:
        field: The form field whose widget attribute will be set.
        attr_name_value (str): A string in the format 'attribute_name:attribute_value'.

    Returns:
        SafeString: The modified form field widget with the new attribute.
    """
    if isinstance(field, SafeString):
        return field
    attr_name, attr_value = attr_name_value.split(':')
    attrs = field.field.widget.attrs.copy()
    attrs[attr_name] = attr_value
    return field.as_widget(attrs=attrs)


@register.filter
def get_item(dictionary, key):
    """
    Retrieve an item from a dictionary by key.

    This filter returns the value associated with the specified key in the dictionary.

    Args:
        dictionary (dict): The dictionary from which to retrieve the item.
        key: The key for the item to retrieve.

    Returns:
        The value associated with the key, or None if the key does not exist.
    """
    return dictionary.get(key)


@register.filter
def instanceof(obj, class_name):
    """
    Check if an object is an instance of a specified class.

    This filter checks if the given object is an instance of the specified class name.

    Args:
        obj: The object to check.
        class_name (str): The name of the class to check against.

    Returns:
        bool: True if the object is an instance of the class, False otherwise.
    """
    return obj.__class__.__name__ == class_name


@register.filter
def is_meeting(value):
    """
    Check if a value is an instance of the Meeting class.

    Args:
        value: The value to check.

    Returns:
        bool: True if the value is an instance of Meeting, False otherwise.
    """
    return isinstance(value, Meeting)


@register.filter
def is_call(value):
    """
    Check if a value is an instance of the Call class.

    Args:
        value: The value to check.

    Returns:
        bool: True if the value is an instance of Call, False otherwise.
    """
    return isinstance(value, Call)


@register.filter
def is_email(value):
    """
    Check if a value is an instance of the Email class.

    Args:
        value: The value to check.

    Returns:
        bool: True if the value is an instance of Email, False otherwise.
    """
    return isinstance(value, Email)


@register.filter
def is_ticket(value):
    """
    Check if a value is an instance of the Ticket class.

    Args:
        value: The value to check.

    Returns:
        bool: True if the value is an instance of Ticket, False otherwise.
    """
    return isinstance(value, Ticket)
