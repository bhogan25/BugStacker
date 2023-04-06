from django.contrib import admin
from .models import User, Project, Workflow, Ticket, Notification

# Register your models here.
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Workflow)
admin.site.register(Ticket)
# admin.site.register(Notification)