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
from .forms import NewTicketForm
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
    if request.method == "GET":
        # project_list = Project.objects.all().filter(pm=request.user.id)
        project_list = request.user.get_all_projects()
        return render(request, 'BUGSTACKER/index.html', {
            "project_list": project_list,
        })


@login_required
def project_board(request, project_code):
    if request.method == "POST":
        pass
    else:

        # Get Project if exists
        project = get_object_or_404(Project, code=project_code)

        # Return view if project in user
        if project in request.user.get_all_projects():
            
            # New Ticket Form
            form = NewTicketForm()
            form.fields.get('workflow').queryset = project.workflows.all()
            form.fields.get('assignees').queryset = project.all_members()
            
            return render(request, 'BUGSTACKER/project-board.html', {
                "project": project,
                "form": form,
            })
        else:
            raise Http404("We couldn't find that project!")

