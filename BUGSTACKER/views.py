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
from .forms import NewTicketForm, NewWorkflowForm, NewProjectForm
from django import forms



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
        print(request.POST.getlist("role"))
        breakpoint
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
            
            project.code = Project.objects.all().count() + 1
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
    
    if request.method == "POST":

        # Collect Post request data
        q_dict = request.POST
        
        
        # Check which form is being submitted (workflow | ticket)
        if len(q_dict) == len(NewTicketForm.Meta.fields) + 1:

            print("----------- NEW TICKET FORM -----------")
            
            # Create new ticket instance
            ticket_form = NewTicketForm(request.POST)
            
            # Clean Model Form and Model Validation
            if ticket_form.is_valid():

                # Create ticket instance
                new_ticket = ticket_form.save(commit=False)

                # Populate private fields
                new_ticket.code = new_ticket.workflow.tickets.count() + 1
                new_ticket.creator = request.user
                new_ticket.resolution = Ticket.Resolution.NOT_FIXED

                # Save new instance and many-to-many data
                new_ticket.save()
                ticket_form.save_m2m()

                return HttpResponseRedirect(reverse("project_board", args=(project_code,)))

            else:
                raise Http404("Submitted data invalid.")

        # If form is Workflow
        elif len(q_dict) == len(NewWorkflowForm.Meta.fields) + 1:

            print("----------- NEW WORKFLOW FORM -----------")
            
            # Create new workflow instance
            workflow_form = NewWorkflowForm(request.POST)

            # Clean Model Form and Model Validation
            if workflow_form.is_valid():

                # Create ticket instance
                new_workflow = workflow_form.save(commit=False)

                # Populate private fields
                new_workflow.project = project
                new_workflow.code = project.workflows.count() + 1
                new_workflow.archived = False

                # Save new instance
                new_workflow.save()

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
            ticket_form = NewTicketForm()
            ticket_form.fields.get('workflow').queryset = project.workflows.all()
            ticket_form.fields.get('assignees').queryset = project.all_members()

            # New Workflow Form
            workflow_form = NewWorkflowForm()
            
            return render(request, 'BUGSTACKER/project-board.html', {
                "project": project,
                "ticket_form": ticket_form,
                "workflow_form": workflow_form,
            })
        else:
            raise Http404("We couldn't find that project!")

