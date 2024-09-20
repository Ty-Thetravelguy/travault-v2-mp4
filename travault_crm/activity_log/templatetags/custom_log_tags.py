from django import template
from django.forms import CheckboxInput, RadioSelect

register = template.Library()

@register.filter(name='add_class')
def add_class(value, css_class):
    if isinstance(value.field.widget, (CheckboxInput, RadioSelect)):
        return value
    return value.as_widget(attrs={"class": css_class})