from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:project_code>", views.project_board, name="project_board"),
    path("accounts/login", views.login_view, name="login"),
    path("accounts/register", views.register, name="register"),
    path("accounts/logout", views.logout_view, name="logout"),
]