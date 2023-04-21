from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("projects/<int:project_code>", views.project_board, name="project_board"),
    path("accounts/login", views.login_view, name="login"),
    path("accounts/register", views.register, name="register"),
    path("accounts/logout", views.logout_view, name="logout"),

    # API Routes
    path("project/<str:action>/<int:project_code>", views.api_project, name="api_project"),
    path("workflow/<str:action>/<int:project_code>/<int:workflow_code>", views.api_workflow, name="api_workflow"),
    path("ticket/<str:action>/<int:project_code>/<int:workflow_code>/<int:ticket_code>", views.api_ticket, name="api_ticket"),
]