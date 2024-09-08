from django import template

register = template.Library()

@register.filter
def split_urls(value, delimiter=','):
    """Splits the input string by the specified delimiter and returns a list."""
    return [url.strip() for url in value.split(delimiter) if url.strip()]

@register.filter
def split_by_comma(value):
    """Splits a string by commas and returns a list."""
    if value:
        return [item.strip() for item in value.split(',') if item.strip()]
    return []
