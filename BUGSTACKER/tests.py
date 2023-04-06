import datetime
from django.test import TestCase, Client
from django.contrib.contenttypes.models import ContentType
from .models import User, Project, Workflow, Ticket, Notification



class BugstackerTestCase(TestCase):

    def setUp(self):

        # Create Users
        user_0 = User.objects.create(
            first_name="Jan",
            last_name="Levinson-Gould",
            username="jan",
            email="janlg@django.com",
            password="123",
            role=User.Role.PROJECT_MANAGER,
        )

        user_1 = User.objects.create(
            first_name="Michael",
            last_name="Scott",
            username="michael",
            email="michael@django.com",
            password="123",
            role=User.Role.DEVELOPER,
        )

        user_2 = User.objects.create(
            first_name="Dwight",
            last_name="Shrute",
            username="dwight",
            email="dwight@django.com",
            password="123",
            role=User.Role.DEVELOPER,
        )

        # Create Users with no project or tickets
        user_free = User.objects.create(
            first_name="Free",
            last_name="Guy",
            username="freeguy",
            email="freeguy@django.com",
            password="123",
            role=User.Role.DEVELOPER,
        )

        # Create Project
        project_1 = Project.objects.create(
            code=1, 
            name="Select New Healthcare Plan",
            completed=False,
            pm=user_0,
            status=Project.Status.ACTIVE,
        )

        # Create Workflows
        workflow_1 = Workflow.objects.create(
            project=project_1,
            code=0,
            name="General",
            description="""A general workflow for tasks 
                that do not belong to any specific 
                category.""",
            archived=False,
        )

        workflow_2 = Workflow.objects.create(
            project=project_1,
            code=1,
            name="Illegitimate Health Conditions",
            description="""There are several health 
                conditions listed that do not exits. 
                We need to interview all employees to check 
                whether or not their health condition is 
                real.""",
            archived=False,
        )

        # Create Tickets
        ticket_1 = Ticket.objects.create(
            workflow=workflow_1,
            creator=user_1,
            code=1,
            name="Recruit Assistant",
            description="""I (Michael) am in need of an 
                assistant to do this project for me 
                because I have more important things to 
                do.""",
            target_complete=datetime.date(2004, 4, 4),
            priority=Ticket.Priority.NORMAL,
            status=Ticket.Status.CREATED,
        )

        ticket_2 = Ticket.objects.create(
            workflow=workflow_2,
            creator=user_2,
            code=1,
            name="Hotdog Fingers",
            description="""Jim says he has hotdog 
                fingers, despite the fact that 
                hotdog fingers is not a diagnosable 
                health condition according to WebMD!
                Get him to admit he is lying, and have 
                him write a formal apology letter to
                the entire office.""",
            target_complete=datetime.date(2004, 4, 4),
            priority=Ticket.Priority.HIGH,
            status=Ticket.Status.CREATED,
        )

        ticket_3 = Ticket.objects.create(
            workflow=workflow_2,
            creator=user_2,
            code=1,
            name="Review with Michael",
            description="""Have Michael review
                the new plan that has been 
                selected.""",
            target_complete=datetime.date(2004, 4, 6),
            priority=Ticket.Priority.NORMAL,
            status=Ticket.Status.CREATED,
        )

        # Create Notification
        notif_1 = Notification.objects.create(
            actor_object_id=user_1.id,
            actor_content_type=ContentType.objects.get_for_model(User),
            recipient=user_0,
            verb="created",
            action_object_object_id=ticket_1.id,
            target_object_id=ticket_1.workflow.id,
            target_content_type=ContentType.objects.get_for_model(Ticket),
            public=True,
        )

        # Create Team
        project_1.team_members.set([user_1, user_2])

        # Designate Assignees for Tickets
        ticket_1.assignees.set([user_1])
        ticket_2.assignees.set([user_2])


    # Test number of Users
    def test_user_count(self):
        num_users = User.objects.all().count()

        self.assertEqual(num_users, 4)

    # Test number of Projects
    def test_project_count(self):
        num_projects = Project.objects.all().count()

        self.assertEqual(num_projects, 1)


    # Test number of Workflows
    def test_workflow_count(self):
        num_workflows = Workflow.objects.all().count()

        self.assertEqual(num_workflows, 2)

    # Test number of all Tickets
    def test_ticket_count(self):
        num_tickets = Ticket.objects.all().count()

        self.assertEqual(num_tickets, 3)

    # Test number of team members
    def test_project_members_count(self):
        num_team_members = Project.objects.first().team_members.count()

        self.assertEqual(num_team_members, 2)

    # Test number of tasks assinged to user
    def test_ticket_assignee_count(self):
        num_assignees_ticket_1 = Ticket.objects.first().assignees.count()

        self.assertEqual(num_assignees_ticket_1, 1)

    # Test retrieve Project PM from ticket
    def get_PM_from_ticket(self):
        ticket_1_PM = Ticket.objects.first().workflow.project.pm

        self.assertEqual(ticket_1_PM.first_name, 'Jan')

    # Test User Notification count
    def test_notification_count(self):
        notif_count = User.objects.get(pk=1).notifications.count()

        self.assertEqual(notif_count, 1)

    # Test project method all_member_usernames
    def test_all_member_usernames(self):
        all_members = Project.objects.get(pk=1).all_member_usernames()

        self.assertEqual(len(all_members), 3)

    # Test project open_tickets method
    def test_open_tickets(self):
        open_tickets = Project.objects.get(pk=1).open_tickets()

        self.assertEqual(open_tickets, 3)

    # Test user method get_all_projects for False
    def test_get_all_projects_false(self):
        all_projects = User.objects.get(username='freeguy').get_all_projects()

        self.assertFalse(all_projects)

    # Test user method get_all_projects for pm
    def test_get_all_projects_pm(self):
        all_projects = User.objects.get(username='jan').get_all_projects()

        self.assertEqual(all_projects.count(), 1)

    # Test user method get_all_projects for pm
    def test_get_all_projects_dev(self):
        all_projects = User.objects.get(username='michael').get_all_projects()

        self.assertEqual(all_projects.count(), 1)