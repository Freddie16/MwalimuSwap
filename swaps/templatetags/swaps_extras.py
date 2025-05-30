# swaps/templatetags/swaps_extras.py

from django import template

register = template.Library()

@register.filter
def split_string(value, arg):
    """
    Splits a string by the given argument.
    Usage: {{ value|split_string:"," }}
    """
    return value.split(arg)

@register.filter
def strip_string(value):
    """
    Strips leading/trailing whitespace from a string.
    Usage: {{ value|strip_string }}
    """
    return value.strip()
