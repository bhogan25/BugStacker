from django import forms
from .models import Ticket, Workflow, Project


class NewProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name',
            'description',
            'team_members',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Project description'}),
            'team_members': forms.SelectMultiple(attrs={'class': 'form-control'})
        }

class NewWorkflowForm(forms.ModelForm,):
    class Meta:
        model = Workflow
        fields = [
            'name',
            'description',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
        }

class NewTicketForm(forms.ModelForm,):
    class Meta:
        model = Ticket
        fields = [
            'name', 
            'workflow', 
            'description', 
            'target_complete', 
            'priority', 
            'assignees',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'workflow': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
            'target_complete': forms.DateInput(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'assignees': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }