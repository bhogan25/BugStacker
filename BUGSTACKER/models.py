from django.db import models
from django.contrib.auth.models import AbstractUser
from notifications.base.models import AbstractNotification


# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        PROJECT_MANAGER = 'PM'
        DEVELOPER = 'DEV'
    
    role = models.CharField(
        choices=Role.choices,
        default=Role.DEVELOPER,
        max_length=3,
    )

    class Meta:
        ordering = ['username']

    # Get projects involved
    def get_all_projects(self):
        return self.projects_managed.all() if self.projects_managed.all() else self.projects_working.all()
    
    def __str__(self):
        return f"{self.username} ({self.role})"

# Project
class Project(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "A"
        INACTIVE = "I"

    code = models.PositiveSmallIntegerField(verbose_name="project code")
    name = models.CharField(max_length=60, verbose_name="project name")
    created = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False, verbose_name="project complete?")
    pm = models.ForeignKey('User', null=True, on_delete=models.SET_NULL, related_name='projects_managed')
    team_members = models.ManyToManyField(User, blank=True, related_name='projects_working')
    status = models.CharField(
            choices=Status.choices,
            default=Status.ACTIVE,
            max_length=2,
        )

    class Meta:
        ordering = ['created']

    # Get open ticket count
    def open_tickets(self):
        return sum([workflow.tickets.count() for workflow in self.workflows.all()])

    # Get team members and pm
    def all_member_usernames(self):
        return [user.username for user in self.team_members.all()] + [self.pm.username]
    
    def __str__(self):
        return f"Project {self.code}"

# Workflow
class Workflow(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name="workflows")
    code = models.PositiveSmallIntegerField(verbose_name="workflow code")
    name = models.CharField(max_length=60, verbose_name="workflow name")
    description = models.TextField(max_length=500, verbose_name="workflow description")
    created = models.DateField(auto_now_add=True)
    archived = models.BooleanField(default=False, verbose_name="workflow archived")

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"Workflow {self.project.code}-{self.code}"

# Ticket
class Ticket(models.Model):
    class Status(models.TextChoices):
        CREATED = "C"
        IN_PROGRESS = "IP"
        DONE = "D"

    class Resolution(models.TextChoices):
        FIXED = "F"
        NO_ISSUE = "NI"
        NOT_FIXED = "NF"

    class Priority(models.IntegerChoices):
        HIGH = 3
        NORMAL = 2
        LOW = 1

    workflow = models.ForeignKey('Workflow', on_delete=models.CASCADE, related_name="tickets")
    creator = models.ForeignKey('User', null=True, on_delete=models.SET_NULL, related_name="tickets_created")
    assignees = models.ManyToManyField(User, blank=True, related_name="tickets_assigned")
    code = models.PositiveSmallIntegerField(verbose_name="ticket code")
    name = models.CharField(max_length=60, verbose_name="ticket name")
    description = models.TextField(max_length=500, verbose_name="ticket description")
    target_complete = models.DateField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    priority = models.PositiveSmallIntegerField(
        choices=Priority.choices, 
        default=Priority.NORMAL,
        )
    status = models.CharField(
        choices=Status.choices, 
        default=Status.CREATED, 
        max_length=2,
        )
    resolution = models.CharField(
        choices=Resolution.choices, 
        max_length=2,
        null=True,
        )
    
    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"Ticket {self.workflow.project.code}-{self.workflow.code}-{self.code}"

# Notifications
class Notification(AbstractNotification):
    pass

    class Meta(AbstractNotification.Meta):
        abstract = False

# Join: User-Notification