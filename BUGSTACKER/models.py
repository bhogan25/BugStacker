from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from notifications.base.models import AbstractNotification


class User(AbstractUser):
    class Role(models.TextChoices):
        PROJECT_MANAGER = 'PM'
        DEVELOPER = 'DEV'
    
    role = models.CharField(
        choices=Role.choices,
        default=Role.DEVELOPER,
        max_length=3,
    )

    # Get projects involved
    def get_all_projects(self):
        return self.projects_managed.all() if self.projects_managed.all() else self.projects_working.all()

    # TODO: Test
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


# Project QuerySet
class ProjectQuerySet(models.QuerySet):

    # Get active projects (active & incomplete)
    def active(self):
        return self.filter(status="A", completed=False)

    # Get completed projects
    def completed(self):
        return self.filter(completed=True)

    # Get on hold projects (inactive & incomplete)
    def on_hold(self):
        return self.filter(status="I", completed=False)

    # Get incomplete projects - TODO: Test
    def incomplete(self):
        return self.filter(completed=False)


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
    team_members = models.ManyToManyField(User, blank=True, related_name='projects_working', verbose_name="Select Team Members")
    description = models.TextField(max_length=500, default="", verbose_name="project description")
    status = models.CharField(
            choices=Status.choices,
            default=Status.ACTIVE,
            max_length=2,
        )

    objects = ProjectQuerySet.as_manager()

    # Get TicketQuerySet for all project's tickets
    def all_tickets(self):
        base = Ticket.objects.none()
        for workflow in self.workflows.all():
            base = base | workflow.tickets.all()
        return base

    # Get User QuerySet of team members and pm
    def all_members(self):
        team_members = self.team_members.all()
        pm = User.objects.filter(id=self.pm.id)
        all_members = team_members | pm
        return all_members

    # TODO: Test
    def long_hrc(self):
        return f"P{self.code}"

    def __str__(self):
        return f"{self.name}"


# Workflow QuerySet
class WorkflowQuerySet(models.QuerySet):

    # Get Active workflows
    def active(self):
        return self.filter(archived=False)

    # Get Archived workflows
    def archived(self):
        return self.filter(archived=True)

# Workflow
class Workflow(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name="workflows")
    code = models.PositiveSmallIntegerField(verbose_name="workflow code")
    name = models.CharField(max_length=60, verbose_name="workflow name")
    description = models.TextField(max_length=500, verbose_name="workflow description")
    created = models.DateField(auto_now_add=True)
    archived = models.BooleanField(default=False, verbose_name="workflow archived")

    objects = WorkflowQuerySet.as_manager()

    # TODO: Test
    def long_hrc(self):
        return f"P{self.project.code}-W{self.code}"

    # TODO: Test
    def short_hrc(self):
        return f"W{self.code}"

    def __str__(self):
        return f"{self.code}: {self.name}"


# Ticket QuerySet
class TicketQuerySet(models.QuerySet):

    # Get open tickets
    def open(self):
        return self.exclude(status="D")

    # Get tickets not started 
    def not_started(self):
        return self.filter(status="C")

    # Get in progres tickets
    def in_progress(self):
        return self.filter(status="IP")

    # Get high priority tickets
    def high_priority(self):
        return self.filter(priority=3)

    # Get normal priority tickets
    def normal_priority(self):
        return self.filter(priority=2)

    # Get low priority tickets
    def low_priority(self):
        return self.filter(priority=1)

    # Get resolved tickets
    def resolved(self):
        return self.filter(status="D")

    # Get resolved & fixed tickets
    def fixed(self):
        return self.filter(status="D").filter(resolution="F")

    # Get resolved and no issue tickets
    def no_issue(self):
        return self.filter(status="D").filter(resolution="NI")


# Ticket
class Ticket(models.Model):
    class Status(models.TextChoices):
        CREATED = "C"
        IN_PROGRESS = "IP"
        DONE = "D"

        @classmethod
        def values_array(cls):
            return [member.value for member in cls]

    class Resolution(models.TextChoices):
        FIXED = "F"
        NO_ISSUE = "NI"
        NOT_FIXED = "NF"

        @classmethod
        def values_array(cls):
            return [member.value for member in cls]

    class Priority(models.IntegerChoices):
        HIGH = 3
        NORMAL = 2
        LOW = 1

    # project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name="tickets")
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

    objects = TicketQuerySet.as_manager()

    # TODO: Test
    def string_assignees(self):
        if self.assignees.all().count() > 0:
            return ", ".join([user.full_name() for user in self.assignees.all()])
        else:
            return None

    # TODO: Test
    def slug_assignees(self):
        if self.assignees.all().count() > 0:
            return "-".join([user.full_name() for user in self.assignees.all()])
        else:
            return None

    # TODO: Test
    def long_hrc(self):
        return f"P{self.workflow.project.code}-W{self.workflow.code}-T{self.code}"

    # TODO: Test
    def short_hrc(self):
        return f"W{self.workflow.code}-T{self.code}"

    def __str__(self):
        return f"Ticket {self.workflow.project.code}-{self.workflow.code}-{self.code}"

# Notifications --- TODO: REMOVE ALL BELOW ---
class Notification(AbstractNotification):


    class Meta(AbstractNotification.Meta):
        abstract = False

# Join: User-Notification