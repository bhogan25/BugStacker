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

        # Create User PM with 1 hold project and 1 finished project only
        user_retired = User.objects.create(
            first_name="Retired",
            last_name="Person",
            username="retiredperson",
            email="retiredperson@django.com",
            password="123",
            role=User.Role.PROJECT_MANAGER,
        )

        # Create Projects
        project_1 = Project.objects.create(
            code=1, 
            name="Select New Healthcare Plan",
            completed=False,
            pm=user_0,
            status=Project.Status.ACTIVE,
        )

        project_2 = Project.objects.create(
            code=2, 
            name="Project On Hold",
            completed=False, 
            pm=user_retired, 
            status=Project.Status.INACTIVE,
        )

        project_3 = Project.objects.create(
            code=3, 
            name="Finished Project",
            completed=True,
            pm=user_retired,
            status=Project.Status.INACTIVE,
        )

        project_4 = Project.objects.create(
            code=4, 
            name="TicketQuerySet Tests",
            completed=False,
            pm=user_retired,
            status=Project.Status.ACTIVE,
        )

        # Create Workflows
        workflow_1_0 = Workflow.objects.create(
            project=project_1,
            code=0,
            name="General",
            description="""A general workflow for tasks 
                that do not belong to any specific 
                category.""",
            archived=False,
        )

        workflow_1_1 = Workflow.objects.create(
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

        workflow_4_0 = Workflow.objects.create(
            project=project_4,
            code=0,
            name="TicketQuerySet Tests Nonarchived Workflow",
            description="""...""",
            archived=False,
        )

        workflow_4_1 = Workflow.objects.create(
            project=project_4,
            code=1,
            name="TicketQuerySet Tests Archived Workflow",
            description="""...""",
            archived=True,
        )

        # Create Tickets
        ticket_1_1_1 = Ticket.objects.create(
            workflow=workflow_1_0,
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

        ticket_1_2_1 = Ticket.objects.create(
            workflow=workflow_1_1,
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

        ticket_1_2_2 = Ticket.objects.create(
            workflow=workflow_1_1,
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

        ticket_4_0_1 = Ticket.objects.create(
            workflow=workflow_4_0,
            creator=user_retired,
            code=1,
            name="Normal & Created Ticket",
            description="""...""",
            target_complete=datetime.date(2004, 4, 4),
            priority=Ticket.Priority.NORMAL,
            status=Ticket.Status.CREATED,
        )

        ticket_4_0_2 = Ticket.objects.create(
            workflow=workflow_4_0,
            creator=user_retired,
            code=2,
            name="High & In Progress Ticket",
            description="""...""",
            target_complete=datetime.date(2004, 4, 4),
            priority=Ticket.Priority.HIGH,
            status=Ticket.Status.IN_PROGRESS,
        )

        ticket_4_0_3 = Ticket.objects.create(
            workflow=workflow_4_0,
            creator=user_retired,
            code=3,
            name="Low & Done & Fixed Ticket",
            description="""...""",
            target_complete=datetime.date(2004, 4, 4),
            priority=Ticket.Priority.LOW,
            status=Ticket.Status.DONE,
            resolution=Ticket.Resolution.FIXED,
        )

        ticket_4_0_4 = Ticket.objects.create(
            workflow=workflow_4_0,
            creator=user_retired,
            code=4,
            name="Low & Done & No Issue Ticket",
            description="""...""",
            target_complete=datetime.date(2004, 4, 4),
            priority=Ticket.Priority.LOW,
            status=Ticket.Status.DONE,
            resolution=Ticket.Resolution.NO_ISSUE,
        )

        # Create Notification
        notif_1 = Notification.objects.create(
            actor_object_id=user_1.id,
            actor_content_type=ContentType.objects.get_for_model(User),
            recipient=user_0,
            verb="created",
            action_object_object_id=ticket_1_1_1.id,
            target_object_id=ticket_1_1_1.workflow.id,
            target_content_type=ContentType.objects.get_for_model(Ticket),
            public=True,
        )

        # Create Team
        project_1.team_members.set([user_1, user_2])

        # Designate Assignees for Tickets
        ticket_1_1_1.assignees.set([user_1])
        ticket_1_2_1.assignees.set([user_2])


    # User Setup and Model Relationships

    # Test number of Users
    def test_user_count(self):
        num_users = User.objects.all().count()

        self.assertEqual(num_users, 5)

    # Test number of Projects
    def test_project_count(self):
        num_projects = Project.objects.all().count()

        self.assertEqual(num_projects, 4)

    # Test number of Workflows
    def test_workflow_count(self):
        num_workflows = Workflow.objects.all().count()

        self.assertEqual(num_workflows, 4)

    # Test number of all Tickets
    def test_ticket_count(self):
        num_tickets = Ticket.objects.all().count()

        self.assertEqual(num_tickets, 7)

    # Test number of team members
    def test_project_members_count(self):
        num_team_members = Project.objects.get(pk=1).team_members.count()

        self.assertEqual(num_team_members, 2)

    # Test number of users assinged to a ticket
    def test_ticket_assignee_count(self):
        num_assignees_ticket_1 = Ticket.objects.first().assignees.count()

        self.assertEqual(num_assignees_ticket_1, 1)

    # Test number of users assigned to a ticket
    def test_user_ticket_count(self):
        user_tickets = User.objects.get(pk=2).tickets_assigned.count()

        self.assertEqual(user_tickets, 1)

    # Test retrieve Project PM from ticket
    def get_PM_from_ticket(self):
        ticket_1_PM = Ticket.objects.first().workflow.project.pm

        self.assertEqual(ticket_1_PM.first_name, 'Jan')

    # Test User Notification count
    def test_notification_count(self):
        notif_count = User.objects.get(pk=1).notifications.count()

        self.assertEqual(notif_count, 1)


    # User Methods

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

    # Project Methods - Tested on Project(pk=1)

    # Test project method all_member_usernames
    def test_all_member_usernames(self):
        all_members = Project.objects.get(pk=1).all_member_usernames()

        self.assertEqual(len(all_members), 3)

    
    # Change Requst: To be changed to return TicketQuerySet of all Project Tickets
    
    # Test project all_tickets method
    # def test_all_tickets(self):
    #     all_tickets = Project.objects.get(pk=1).all_tickets()

    #     self.assertEqual(all_tickets, 3)




    # ProjectQuerySet Methods - Tested on all Projects

    # Test active method
    def test_ProjectQuerySet_active(self):
        active_projects = Project.objects.all().active().count()

        self.assertEqual(active_projects, 2)

    # Test finished method
    def test_ProjectQuerySet_finished(self):
        finished_projects = Project.objects.all().finished().count()

        self.assertEqual(finished_projects, 1)

    # Test on_hold method
    def test_ProjectQuerySet_on_hold(self):
        on_hold_projects = Project.objects.all().on_hold().count()
        
        self.assertEqual(on_hold_projects, 1)


    # TicketQuerySet Methods - Tested on all Workflow 4-0 Tickets

    # Test not_done method
    def test_TicketQuerySet_not_done(self):
        not_done = Workflow.objects.get(
            name="TicketQuerySet Tests Nonarchived Workflow"
        ).tickets.all().not_done().count()

        self.assertEqual(not_done, 2)

    # Test not_started method
    def test_TicketQuerySet_not_started(self):
        not_started = Workflow.objects.get(
            name="TicketQuerySet Tests Nonarchived Workflow"
        ).tickets.all().not_started().count()

        self.assertEqual(not_started, 1)

    # Test in_progress method
    def test_TicketQuerySet_in_progress(self):
        in_progress = Workflow.objects.get(
            name="TicketQuerySet Tests Nonarchived Workflow"
        ).tickets.all().in_progress().count()

        self.assertEqual(in_progress, 1)

    # Test high_priority method
    def test_TicketQuerySet_high_priority(self):
        high_priority = Workflow.objects.get(
            name="TicketQuerySet Tests Nonarchived Workflow"
        ).tickets.all().high_priority().count()

        self.assertEqual(high_priority, 1)

    # Test normal_priority method
    def test_TicketQuerySet_normal_priority(self):
        normal_priority = Workflow.objects.get(
            name="TicketQuerySet Tests Nonarchived Workflow"
        ).tickets.all().normal_priority().count()

        self.assertEqual(normal_priority, 1)

    # Test low_priority method
    def test_TicketQuerySet_low_priority(self):
        low_priority = Workflow.objects.get(
            name="TicketQuerySet Tests Nonarchived Workflow"
        ).tickets.all().low_priority().count()

        self.assertEqual(low_priority, 2)

    # Test resolved method
    def test_TicketQuerySet_resolved(self):
        resolved = Workflow.objects.get(
            name="TicketQuerySet Tests Nonarchived Workflow"
        ).tickets.all().resolved().count()

        self.assertEqual(resolved, 2)

    # Test fixed method
    def test_TicketQuerySet_fixed(self):
        fixed = Workflow.objects.get(
            name="TicketQuerySet Tests Nonarchived Workflow"
        ).tickets.all().fixed().count()

        self.assertEqual(fixed, 1)

    # Test no_issue method
    def test_TicketQuerySet_no_issue(self):
        no_issue = Workflow.objects.get(
            name="TicketQuerySet Tests Nonarchived Workflow"
        ).tickets.all().no_issue().count()

        self.assertEqual(no_issue, 1)