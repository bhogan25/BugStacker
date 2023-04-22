import json
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .models import User, Project, Workflow, Ticket, Notification
from django.views.decorators.csrf import csrf_exempt
from .forms import NewTicketForm, NewWorkflowForm, NewProjectForm, EditProjectForm
from django import forms


# API Error Response Messages
JSON_ERROR_MESSAGES = {
    "invalid_action": {"error": "Invalid action."},
    "access_denied": {"error": "Access denied."},
    "invalid_payload": {"error": "Invalid payload."}
}

# API Access Permissions
# ----------------------
# Project API
PROJECT_API_ALLOWED_ACTIONS = ['change_status', 'complete']
PROJECT_API_ALLOWED_STATUSES = [Project.Status.ACTIVE, Project.Status.INACTIVE]

# Workflow API

# Ticket API



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "BUGSTACKER/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "BUGSTACKER/login.html")

def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        manager = request.POST.getlist("role")

        if manager:
            role = User.Role.PROJECT_MANAGER
        else:
            role = User.Role.DEVELOPER

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "BUGSTACKER/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(
                username=username, 
                email=email,
                password=password,
                first_name=first_name, 
                last_name=last_name, 
                role=role,
            )
            user.save()
        except IntegrityError:
            return render(request, "BUGSTACKER/register.html", {
                "message": "Username already taken."
            })
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "BUGSTACKER/register.html", {

        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


@login_required
def index(request):
    if request.method == "POST":
        
        project_form = NewProjectForm(request.POST)

        # Verify and clean form data
        if project_form.is_valid():

            # Create project instance
            project = project_form.save(commit=False)
            
            project.code = Project.objects.all().count() + 1     # Fix
            project.completed = False
            project.pm = request.user
            project.status = Project.Status.ACTIVE

            print("-----------NEW PROJECT SUBMITTED-----------")

        else:
            raise Http404("Submitted data invalid.")



    
    if request.method == "GET":
        # Get all user projects
        project_list = request.user.get_all_projects()

        # NewProjectForm setup
        if request.user.role == "PM":

            project_form = NewProjectForm()

            # Get all devs
            devs = User.objects.filter(role="DEV")

            # Set queryset for team_members
            project_form.fields.get('team_members').queryset = devs
        
        else:
            project_form = None

        return render(request, 'BUGSTACKER/index.html', {
            "project_list": project_list,
            "project_form": project_form,
        })


@login_required
def project_board(request, project_code):

    # Get Project if exists
    project = get_object_or_404(Project, code=project_code)

    # If completed project access via URL
    if project.completed == True:
        return render(request, 'BUGSTACKER/error.html', {
            "message": "Project has already been completed."
        })

    if request.method == "POST":

        # Check which form is being submitted (edit project | new workflow | new ticket)
        if (request.POST['target'] == 'ticket' and request.POST['action'] == 'new'):

            print("----------- NEW TICKET FORM -----------")

            # Create new ticket instance
            ticket_form = NewTicketForm(request.POST)

            # Clean Model Form and Model Validation
            if ticket_form.is_valid():

                # Create ticket instance
                new_ticket = ticket_form.save(commit=False)

                # Populate private fields
                new_ticket.code = new_ticket.workflow.tickets.count() + 2     # Fix - come up with hidden token or string (00-00-001, where 001 is the ticket portion and the code value is actually 1 which is the primary key)
                new_ticket.creator = request.user
                new_ticket.resolution = Ticket.Resolution.NOT_FIXED

                # Save new instance and many-to-many data
                new_ticket.save()
                ticket_form.save_m2m()

                return HttpResponseRedirect(reverse("project_board", args=(project_code,)))

            else:
                raise Http404("Submitted data invalid.")

        # If form is New Workflow
        elif (request.POST['target'] == 'workflow' and request.POST['action'] == 'new'):

            print("----------- NEW WORKFLOW FORM -----------")
            
            # Create new workflow instance
            workflow_form = NewWorkflowForm(request.POST)

            # Clean Model Form and Model Validation
            if workflow_form.is_valid():

                # Create ticket instance
                new_workflow = workflow_form.save(commit=False)

                # Populate private fields
                new_workflow.project = project
                new_workflow.code = project.workflows.count() + 1      # Fix
                new_workflow.archived = False

                # Save new instance
                new_workflow.save()

                return HttpResponseRedirect(reverse("project_board", args=(project_code,)))

            else:
                raise Http404("Submitted data invalid.")
        
        # If form is Edit Project
        elif (request.POST['target'] == 'project' and request.POST['action'] == 'edit'):

            print("----------- EDIT PROJECT FORM -----------")
            
            # Check & clean form
            edit_project_form = EditProjectForm(request.POST)

            # Clean Model Form and Model Validation
            if edit_project_form.is_valid():
                if edit_project_form.cleaned_data['name'] != '':
                    project.name = edit_project_form.cleaned_data['name']
                    print(project.name, edit_project_form.cleaned_data['name'])
                
                if edit_project_form.cleaned_data['description'] != '':
                    project.description = edit_project_form.cleaned_data['description']
                    print(project.description, edit_project_form.cleaned_data['description'])

                if edit_project_form.cleaned_data['team_members'] != '':
                    project.team_members.set(edit_project_form.cleaned_data['team_members'])
                    print(edit_project_form.cleaned_data['team_members'])

                project.save()

                return HttpResponseRedirect(reverse("project_board", args=(project_code,)))

            else:
                raise Http404("Submitted data invalid.")
        
        else:
            raise Http404("Submitted data invalid")
        

    # GET Requests
    else:
        
        # Return view if project in user
        if project in request.user.get_all_projects():

            # New Ticket Form
            new_ticket_form = NewTicketForm()
            new_ticket_form.fields.get('workflow').queryset = project.workflows.all()
            new_ticket_form.fields.get('assignees').queryset = project.all_members()

            # New Workflow Form
            new_workflow_form = NewWorkflowForm()

            # Edit Project Form
            edit_project_form = EditProjectForm()
            
            return render(request, 'BUGSTACKER/project-board.html', {
                "project": project,
                "new_ticket_form": new_ticket_form,
                "new_workflow_form": new_workflow_form,
                "edit_project_form": edit_project_form,
            })
        else:
            raise Http404("We couldn't find that project!")


# APIs
@csrf_exempt
@login_required
def api_project(request, action, project_code):

    # Check if action is allowed
    if action not in PROJECT_API_ALLOWED_ACTIONS:
        return JsonResponse(JSON_ERROR_MESSAGES["invalid_action"])
    
    # Get Project
    project = get_object_or_404(Project, code=project_code)

    # Check who is accessing (must be project PM)
    if project.pm != request.user:
        return JsonResponse(JSON_ERROR_MESSAGES["access_denied"])

    # Change Project Status
    if action == 'change_status':
        data = json.loads(request.body)
        current_status = data.get("current_status")

        # Check status returned is allowed
        if current_status not in PROJECT_API_ALLOWED_STATUSES:
            return JsonResponse(JSON_ERROR_MESSAGES['invalid_payload'])
        
        # Select new Project Status
        if current_status == Project.Status.ACTIVE:
            new_status = Project.Status.INACTIVE
            
        elif current_status == Project.Status.INACTIVE:
            new_status = Project.Status.ACTIVE

        # Change project status
        project.status = new_status
        project.save()

        return JsonResponse({
            "message": f"{action.capitalize()} request made on Project: {project.name} (Code: {project.code}) to change status from {current_status} to {new_status}"
        })

    # Complete Project
    if action == 'complete':
        return JsonResponse({
            "message": f"{action.capitalize()} request made on Project: {project.name}, Code: {project.code}"
        })



@csrf_exempt
@login_required
def api_workflow(request, action, project_code, workflow_code):
    workflow = Project\
        .objects.get(code=project_code)\
        .workflows.get(code=workflow_code)
    
    print(f"{action.capitalize()} request made on Workflow: {workflow.name}, Code: {workflow.code}")
    return JsonResponse({"message": f"{action.capitalize()} request made on Workflow: {workflow.name}, Code: {workflow.code}"})


@csrf_exempt
@login_required
def api_ticket(request, action, project_code, workflow_code, ticket_code):
    ticket = Project\
        .objects.get(code=project_code)\
        .workflows.get(code=workflow_code)\
        .tickets.get(code=ticket_code)
    
    print(f"{action.capitalize()} request made on Ticket: {ticket.name}, Code: {ticket.code}")
    return JsonResponse({"message": f"{action.capitalize()} request made on Ticket: {ticket.name}, Code: {ticket.code}"})