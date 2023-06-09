import json
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from .models import User, Project, Workflow, Ticket, Notification
from django.views.decorators.csrf import csrf_exempt
from .forms import NewTicketForm, NewWorkflowForm, NewProjectForm, EditProjectForm, EditWorkflowForm, EditTicketForm
from django import forms
from BUGSTACKER.helpers import generate_ticket_code, generate_wf_code, generate_project_code, extract_mrc_from_hrc, clean_choice_field_data
from BUGSTACKER.api_config import JSON_ERROR_MESSAGES, PROJECT_API_ALLOWED_ACTIONS, WORKFLOW_API_ALLOWED_ACTIONS, TICKET_API_ALLOWED_ACTIONS


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

        # TODO: Check if user is in users model
        if request.user not in User.objects.all():
            raise Http404("Not Found")

        # TODO: Check if user is PM
        if request.user.role != "PM":
            raise Http404("Not Found")

        # Get all user projects
        project_list = request.user.get_all_projects()

        project_form = NewProjectForm(request.POST)

        # Verify and clean form data
        if project_form.is_valid():

            # Create project instance
            project = project_form.save(commit=False)

            project.code = generate_project_code()
            project.completed = False
            project.pm = request.user
            project.status = Project.Status.ACTIVE

            project.save()

            print("-----------NEW PROJECT SUBMITTED-----------")

            return render(request, 'BUGSTACKER/index.html', {
                "project_list": project_list,
                "project_form": project_form,
            })

        else:
            raise Http404("Submitted data invalid.")

    if request.method == "GET":
        # Get all user projects
        project_list = request.user.get_all_projects().incomplete()
        history = request.user.get_all_projects().completed()

        # NewProjectForm setup
        if request.user.role == "PM":

            project_form = NewProjectForm()

            # Set queryset for team_members
            project_form.fields.get('team_members').queryset = User.objects.filter(role="DEV")

        else:
            project_form = None

        return render(request, 'BUGSTACKER/index.html', {
            "project_list": project_list,
            "project_form": project_form,
            "history": history,
        })

@login_required
def project_board(request, project_code):

    # Get Project if exists
    project = get_object_or_404(Project, code=project_code)

    # Block request if project completed
    if project.completed == True:
        return render(request, 'BUGSTACKER/error.html', {
            "message": "Project has already been completed."
        })

    # Check if requester is on project team or is PM
    if request.user not in project.team_members.all() and request.user != project.pm:
        raise Http404("You do not have access to this Project")


    if request.method == "POST":

        # Check if project is active -- TODO: Enforce on front end: When project is Deactivated -> deactivate certain buttons. Also on loading page (template or .onload)
        if project.status == Project.Status.INACTIVE:
            raise Http404("Bad request")

        # Check which form is being submitted (new ticket | new workflow | edit project)
        if (request.POST['target'] == 'ticket' and request.POST['action'] == 'new'):

            print("----------- NEW TICKET FORM -----------")

            # Create new ticket instance
            ticket_form = NewTicketForm(request.POST)

            # Clean Model Form and Model Validation
            if ticket_form.is_valid():

                # Create ticket instance
                new_ticket = ticket_form.save(commit=False)

                # Populate private fields
                new_ticket.code = generate_ticket_code(new_ticket)
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
                new_workflow.code = generate_wf_code(new_workflow)
                new_workflow.archived = False

                # Save new instance
                new_workflow.save()

                return HttpResponseRedirect(reverse("project_board", args=(project_code,)))

            else:
                raise Http404("Submitted data invalid.")

        # If form is Edit Project
        elif (request.POST['target'] == 'project' and request.POST['action'] == 'edit'):

            print("----------- EDIT PROJECT FORM -----------")

            # Check if requester is a PM
            if request.user.role != "PM":
                return Http404("Permission denied")

            # Check & clean form
            edit_project_form = EditProjectForm(request.POST)

            # Clean Model Form and Model Validation
            if edit_project_form.is_valid():

                # New Project data vars
                new_name = edit_project_form.cleaned_data['name']
                new_desc = edit_project_form.cleaned_data['description']
                new_pm = edit_project_form.cleaned_data['pm']
                new_team_members = edit_project_form.cleaned_data['team_members']

                if new_name != '' and new_name != project.name:
                    project.name = new_name
                    print(f"New Project Name: {project.name}")

                if new_desc != '' and new_desc != project.description:
                    project.description = new_desc
                    print(f"New Project Description: {project.description}")

                # Check if new PM is new and has PM status
                if new_pm != '' and new_pm != project.pm and new_pm.role == "PM":
                    project.pm = new_pm
                    print(f"New PM: {edit_project_form.cleaned_data['pm']}")

                if new_team_members.exists():

                    # Compare new and team members
                    print(f"Existing team members: {project.team_members.all()}")
                    print(f"Proposed team members: {new_team_members}")

                    # Users removed
                    removed = [user for user in project.team_members.all() if user not in new_team_members]
                    print(f"Removed Team Members: {removed}")

                    # Users added
                    added = [user for user in new_team_members if user not in project.team_members.all()]
                    print(f"Added Team Members: {added}")

                    # Set new project team members
                    project.team_members.set(new_team_members)

                # Save new project data
                project.save()

                return HttpResponseRedirect(reverse("project_board", args=(project_code,)))

            else:
                raise Http404("Submitted data invalid.")

        # If form is Edit Workflow
        elif (request.POST['target'] == 'workflow' and request.POST['action'] == 'edit'):

            print("----------- EDIT WORKFLOW FORM -----------")

            # Check & clean form
            edit_workflow_form = EditWorkflowForm(request.POST)

            # Declare choices for form field ((code, name), ...)
            options = [(f"W{wf.code}", wf.name) for wf in project.workflows.all()]
            edit_workflow_form.fields.get('edit_workflow').choices = options

            # Clean Model Form and Model Validation
            if edit_workflow_form.is_valid():

                # New Workflow data and vars
                target_wf_hrc = edit_workflow_form.cleaned_data['edit_workflow']       # FIX - rename variable and all instances to edit_workflow_id
                new_name = edit_workflow_form.cleaned_data['name']
                new_desc = edit_workflow_form.cleaned_data['description']

                # Try to extract Machine Resource Codes                             TEST: should properly extract the mrc from the hrc and throw error if proper codes are not present
                try:
                    print(target_wf_hrc)
                    mrcs = extract_mrc_from_hrc(target_wf_hrc)
                    print(mrcs)
                    wf_mrc = mrcs["W"]
                    print(wf_mrc)
                except Exception as e:
                    print(e)
                    return HttpResponseBadRequest("Unable to process form data")

                # Check if workflow exists
                if project.workflows.filter(code=wf_mrc).exists():  # TEST: Should exist

                    # Get workflow object
                    target_wf_obj = project.workflows.filter(code=wf_mrc)[0]  # TEST: Should return valid & correct object

                    # Check if workflow belongs to project
                    if target_wf_obj.project != project:
                        raise Http404("Cannot edit this workflow from this page")

                    if new_name != '' and new_name != target_wf_obj.name:
                        target_wf_obj.name = new_name

                    if new_desc != '' and new_name != target_wf_obj.description:
                        target_wf_obj.description = new_desc

                    # Save new instance
                    target_wf_obj.save()

                    return HttpResponseRedirect(reverse("project_board", args=(project_code,)))

            else:
                print(f'Unable to submit EDIT WORKFLOW FORM {edit_workflow_form.errors}')
                raise Http404("Submitted data invalid")

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
            dev_users = User.objects.filter(role="DEV")
            edit_project_form.fields.get('team_members').queryset = dev_users
            select_size = dev_users.count() if dev_users.count() <= 8 else 8
            edit_project_form.fields.get('team_members').widget.attrs = {'class': 'form-control', 'size': select_size}
            edit_project_form.fields.get('pm').queryset = User.objects.filter(role=User.Role.PROJECT_MANAGER)
            edit_project_form.fields.get('pm').empty_label = None

            # Edit Workflow Form
            edit_workflow_form = EditWorkflowForm()
            options = [(f"W{wf.code}", wf.name) for wf in project.workflows.all()]
            edit_workflow_form.fields.get('edit_workflow').choices = options

            edit_workflow_form.fields.get('edit_workflow').widget.attrs = {'class': 'form-control', 'size': 1, 'id': 'editWorkflowFormSelectWorkflow'}
            edit_workflow_form.fields.get('edit_workflow').empty_label = None

            # Edit Ticket Form
            edit_ticket_form = EditTicketForm()
            edit_ticket_form.fields.get('assignees').queryset = project.all_members()

            # Resolution Options
            resolutions = Ticket.Resolution


            return render(request, 'BUGSTACKER/project-board.html', {
                "project": project,
                "new_ticket_form": new_ticket_form,
                "new_workflow_form": new_workflow_form,
                "edit_project_form": edit_project_form,
                "edit_workflow_form": edit_workflow_form,
                "edit_ticket_form": edit_ticket_form,
                "resolutions": resolutions,
            })
        else:
            raise Http404("We couldn't find that project!")


@csrf_exempt
@login_required
def edit_ticket(request, project_code):

    if request.method == "POST" and request.POST['target'] == 'ticket' and request.POST['action'] == 'edit':

        print("----------- EDIT TICKET FORM -----------")

        # Get Project
        project = get_object_or_404(Project, code=project_code)

        # Block request if project completed
        if project.completed == True:
            raise Http404("Could not process request")

        # Block request if requester is not on project team or is not PM
        if request.user not in project.team_members.all() and request.user != project.pm:
            raise Http404("You do not have access to this Project")

        # Clean form data
        edit_ticket_form = EditTicketForm(request.POST)

        if edit_ticket_form.is_valid():

            # Get form data
            ticket_hrc = edit_ticket_form.cleaned_data['ticket_short_hrc']
            new_description = edit_ticket_form.cleaned_data['description']
            new_assignees = edit_ticket_form.cleaned_data['assignees']

            # Check if ticket HRC is valid
            try:
                mrc = extract_mrc_from_hrc(ticket_hrc)
                target_wf_mrc = mrc["W"]
                target_ticket_mrc = mrc["T"]
            except Exception as e:
                raise Http404(e)

            # Check if ticket exists
            try:
                target_ticket_obj = Workflow.objects.get(project=project, code=target_wf_mrc).tickets.get(code=target_ticket_mrc)
            except MultipleObjectsReturned:
                raise Http404("")
            except ObjectDoesNotExist:
                raise Http404("Ticket does not exist")

             # Block request if Ticket status is "DONE"
            if target_ticket_obj.status == "DONE": 
                raise Http404("Cannot edit closed ticket")

            # Check if description is same as before, or if it is blank
            if new_description != '' and new_description != target_ticket_obj.description:
                target_ticket_obj.description = new_description

            # Check if new assingees are sumbitted
            if new_assignees.exists():

                    # Var declarations
                    team_members = project.all_members()
                    existing_assignees = target_ticket_obj.assignees.all()

                    # Check if new members are on project team
                    for user in new_assignees:
                        if user not in team_members:
                            raise Http404("Proposed assignees not on project team")

                    # Users removed
                    removed = [user for user in existing_assignees if user not in new_assignees]
                    print(f"Removed Assignees: {removed}")

                    # Users added
                    added = [user for user in new_assignees if user not in existing_assignees]
                    print(f"Added Assignees: {added}")

                    # Save new ticket and set new assignees
                    target_ticket_obj.save()
                    target_ticket_obj.assignees.set(new_assignees)

        return HttpResponseRedirect(reverse("project_board", args=(project_code,)))

    else:
        raise Http404("Cannot support that request")


# APIs
@csrf_exempt
@login_required
def api_project(request, action, project_code):

    # Check if action is allowed
    if action not in PROJECT_API_ALLOWED_ACTIONS:
        return JsonResponse(JSON_ERROR_MESSAGES["invalid_action"])

    # Get Project
    try:
        project = Project.objects.get(code=project_code)
    except MultipleObjectsReturned:
        return JsonResponse(JSON_ERROR_MESSAGES["mulitple_objects"])
    except ObjectDoesNotExist:
        return JsonResponse(JSON_ERROR_MESSAGES["object_does_not_exist"])
    except Exception as e:
        print(f"Encountered Error: {e}")
        return JsonResponse(JSON_ERROR_MESSAGES["unknown_error"])

    # Ensure only Project PM allowed
    if project.pm != request.user:
        return JsonResponse(JSON_ERROR_MESSAGES["access_denied"])

    # Change Project Status Request
    if action == 'change_status':

        # Get new Project Status
        new_status = (lambda: Project.Status.ACTIVE, lambda: Project.Status.INACTIVE)[project.status == Project.Status.ACTIVE]()

        # Save new project status
        project.status = new_status
        project.save()

        return JsonResponse({
            "message": f"SERVER: {action.capitalize()} request made on {project.long_hrc()} \
                        to change status from {project.status} to {new_status}."
        })

    # Complete Project Request
    if action == 'complete':

        # Check that project isn't already completed
        if project.completed:
            return JsonResponse({JSON_ERROR_MESSAGES["invalid_action"]})

        # Check that project is not active
        if project.status == Project.Status.ACTIVE:
            return JsonResponse(JSON_ERROR_MESSAGES["invalid_action"])

        # Complete project
        project.completed = True
        project.save()

        return JsonResponse({
            "message": f"SERVER: {action.capitalize()} request made on Project {project.long_hrc()}"
        })


@csrf_exempt
@login_required
def api_workflow(request, action, project_code, workflow_code):

    # Check action
    if action not in WORKFLOW_API_ALLOWED_ACTIONS:
            return JsonResponse(JSON_ERROR_MESSAGES["invalid_action"])

    # Get workflow and project objects
    try:
        target_wf_obj = Project.objects.get(code=project_code).workflows.get(code=workflow_code)
        project = target_wf_obj.project
    except MultipleObjectsReturned:
        return JsonResponse(JSON_ERROR_MESSAGES["mulitple_objects"])
    except ObjectDoesNotExist:
        return JsonResponse(JSON_ERROR_MESSAGES["object_does_not_exist"])
    except Exception as e:
        print(f"Encountered Error: {e}")
        return JsonResponse(JSON_ERROR_MESSAGES["unknown_error"])

    # Check who is accessing (must be project PM or team member)
    if request.user != project.pm and request.user not in project.team_members.all():
        return JsonResponse(JSON_ERROR_MESSAGES["access_denied"])

    # Change Workflow archive state
    if action == 'change_archive_state':

        # Save new Workflow archive state to opposite
        target_wf_obj.archived = False if target_wf_obj.archived else True
        target_wf_obj.save()

    print(f"{action.capitalize()} request made on {target_wf_obj.long_hrc()}")
    return JsonResponse({
        "message": f"{action.capitalize()} request made on {target_wf_obj.long_hrc()}"
    })


@csrf_exempt
@login_required
def api_ticket(request, action, project_code, workflow_code, ticket_code):

    # Check action
    if action not in TICKET_API_ALLOWED_ACTIONS:
        return JsonResponse(JSON_ERROR_MESSAGES["invalid_action"])

    # Check if request.user exists
    if request.user not in User.objects.all():
        print(f"Failed user existance test")
        return JsonResponse(JSON_ERROR_MESSAGES["access_denied"])

    # Check if ticket, workflow and project exists
    try:
        target_ticket_obj = Project\
        .objects.get(code=project_code)\
        .workflows.get(code=workflow_code)\
        .tickets.get(code=ticket_code)
    except MultipleObjectsReturned:
        return JsonResponse(JSON_ERROR_MESSAGES["mulitple_objects"])
    except ObjectDoesNotExist:
        return JsonResponse(JSON_ERROR_MESSAGES["object_does_not_exist"])
    except Exception as e:
        print(f"Encountered Error: {e}")
        return JsonResponse(JSON_ERROR_MESSAGES["unknown_error"])

    # Check if user is on project team
    if request.user not in target_ticket_obj.workflow.project.all_members():
        print(f"Failed user permission test. Not on this project")
        return JsonResponse(JSON_ERROR_MESSAGES["access_denied"])

    # Check if user is PM or Ticket assingee --- TODO: Need to enforce via on front end w/ JS
    if request.user not in target_ticket_obj.assignees.all() and request.user.role != "PM":
        print(f"Failed user permission test. User is not PM or assigned to this ticket")
        return JsonResponse(JSON_ERROR_MESSAGES["access_denied"])

    # Check if workflow is archived             TODO: Enforce on front end w/ JS
    if target_ticket_obj.workflow.archived:
        print(f"Failed user permission test. User is not PM or assigned to this ticket")
        return JsonResponse(JSON_ERROR_MESSAGES["invalid_action"])


    # Harvest request body
    data = json.loads(request.body)

    # Clean client data
    new_status = clean_choice_field_data(data["ticketStatus"], Ticket.Status)
    new_resolution = clean_choice_field_data(data["resolution"], Ticket.Resolution)

    # Interpret requested status change
    if new_status == 'IP':

        # Set status & save ticket
        target_ticket_obj.status = new_status
        target_ticket_obj.save()

        # Send success Response
        return JsonResponse({
            "message": f"SERVER: {action.capitalize()} request on \
                        {target_ticket_obj.long_hrc()} successfull. New Status is \
                        {target_ticket_obj.status}."
        })

    if data["ticketStatus"] == 'D' and new_resolution:

        # Set resolution and status
        target_ticket_obj.resolution = new_resolution
        target_ticket_obj.status = new_status

        # Save Ticket
        target_ticket_obj.save()

        # Send success Response
        return JsonResponse({
            "message": f"SERVER: {action.capitalize()} request on \
                        {target_ticket_obj.long_hrc()} successfull. New Status is \
                        {target_ticket_obj.status} and Resolution is \
                        {target_ticket_obj.resolution}."
        })

    # Else send error response
    print(f"No action taken on ticket {target_ticket_obj.long_hrc()}")
    return JsonResponse({
        "error": f"SERVER: Request made on Ticket: {target_ticket_obj.code} failed."
    })