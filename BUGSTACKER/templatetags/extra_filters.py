# import os
# import sys

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PARENT_DIR = os.path.join(BASE_DIR, "..")
# sys.path.append(PARENT_DIR)

from django import template
from django.template.defaultfilters import stringfilter
from BUGSTACKER.models import Workflow, Ticket

register = template.Library()


@register.filter
@stringfilter
def underscore_to_title(str):
    str_spaced = [' ' if char == "_" else char for char in str]
    return ''.join(str_spaced).title()

# Human readable resource code filters
@register.filter(name="project_hrc")
def project_hrc(project_code):
    return f"P{project_code}"

@register.filter(name="wf_hrc_long")
def wf_hrc_long(wf_code, wf_id):
    wf_project_code = Workflow.objects.get(id=wf_id).project.code
    return f"P{wf_project_code}-W{wf_code}"

@register.filter(name="wf_hrc_short")
def wf_hrc_short(wf_code, wf_id):
    return f"W{wf_code}"

@register.filter(name="ticket_hrc_long")
def ticket_hrc_long(ticket_code, ticket_id):
    ticket_wf_code = Ticket.objects.get(id=ticket_id).workflow.code
    ticket_project_code = Ticket.objects.get(id=ticket_id).workflow.project.code
    return f"P{ticket_project_code}-W{ticket_wf_code}-T{ticket_code}"

@register.filter(name="ticket_hrc_short")
def ticket_hrc_short(ticket_code, ticket_id):
    ticket_wf_code = Ticket.objects.get(id=ticket_id).workflow.code
    return f"W{ticket_wf_code}-T{ticket_code}"

@register.filter(name="percentage")
def percentage(numerator, denominator):
    try:
        n = float(numerator)
        d = float(denominator)
    except ValueError:
        return ""

    if n or d == 0:
        return ""

    return f"{round((n/d)*100, 2)}%"