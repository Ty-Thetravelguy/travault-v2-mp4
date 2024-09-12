from django import template
from django.forms import CheckboxInput, RadioSelect
from django.utils.safestring import SafeString

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    if isinstance(value, SafeString):
        return value
    if isinstance(value.field.widget, (CheckboxInput, RadioSelect)):
        return value
    existing_classes = value.field.widget.attrs.get('class', '')
    new_classes = f"{existing_classes} {css_class}".strip()
    return value.as_widget(attrs={"class": new_classes})

@register.filter(name='attr')
def set_attr(field, attr_name_value):
    if isinstance(field, SafeString):
        return field
    attr_name, attr_value = attr_name_value.split(':')
    attrs = field.field.widget.attrs.copy()
    attrs[attr_name] = attr_value
    return field.as_widget(attrs=attrs)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

