from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def underscore_to_title(str):
    str_spaced = [' ' if char == "_" else char for char in str]
    return ''.join(str_spaced).title()

