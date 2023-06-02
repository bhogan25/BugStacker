import re
from .models import Project

# Ensures new Ticket code is not duplicated
def generate_ticket_code(new_ticket_instance):
    if new_ticket_instance.workflow.tickets.count() == 0:
        return 1
    else:
        return max([t.code for t in new_ticket_instance.workflow.tickets.all()]) + 1


# Ensures new Workflow code is not duplicated
def generate_wf_code(new_wf_instance):
    if new_wf_instance.project.workflows.count() == 0:
        return 0
    else: 
        return max([wf.code for wf in new_wf_instance.project.workflows.all()]) + 1


# Ensures new Project code is not duplicated
def generate_project_code():
    return 1 if Project.objects.count() == 0 else max([p.code for p in Project.objects.all()]) + 1


# Checks and extracts the machine resource codes (mrc) from the human resource codes (hrc) 
# Ex: P1-W0-T1 -> {'P': 1, 'W': 0, 'T': 1}
def extract_mrc_from_hrc(re_code):

    # Search for full match
    reg_ex = "^(P[0-9]+)(-W[0-9]+){1}(-T[0-9]+)?|^(W[0-9]+){1}(-T[0-9]+)?|^(P[0-9]+)"
    match = re.fullmatch(reg_ex, re_code)

    # If match, load into dictionary and return
    if match:
        sections = re.split("-", match.group())
        codes = {i[:1]: i[1:] for i in sections}
        return codes
    else:
        raise Exception("HRC code does not match standard pattern")


# Returns a safe version of a client's choice of a model choice field
def clean_choice_field_data(raw_value, Model):
    try:
        model_values = [value for value in Model]
        target_value_index = model_values.index(raw_value)
        return model_values[target_value_index]
    except Exception as e:
        return None
