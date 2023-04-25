from django import forms
from .models import Ticket, Workflow, Project


class NewProjectForm(forms.ModelForm):
    action = forms.CharField(widget=forms.HiddenInput(attrs={'value': 'new'}))
    target = forms.CharField(widget=forms.HiddenInput(attrs={'value': 'project'}))

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
            'team_members': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class EditProjectForm(forms.ModelForm):
    action = forms.CharField(widget=forms.HiddenInput(attrs={'value': 'edit'}))
    target = forms.CharField(widget=forms.HiddenInput(attrs={'value': 'project'}))

    class Meta:
        model = Project
        fields = [
            'name',
            'description',
            'pm',
            'team_members',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Project description'}),
            'pm': forms.Select(attrs={'class': 'form-control'}),
            'team_members': forms.SelectMultiple(),
        }


class NewWorkflowForm(forms.ModelForm):
    action = forms.CharField(widget=forms.HiddenInput(attrs={'value': 'new'}))
    target = forms.CharField(widget=forms.HiddenInput(attrs={'value': 'workflow'}))

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

class EditWorkflowForm(NewWorkflowForm):
    action = forms.CharField(widget=forms.HiddenInput(attrs={'value': 'edit'}))
    workflow = forms.ChoiceField()


class NewTicketForm(forms.ModelForm,):
    action = forms.CharField(widget=forms.HiddenInput(attrs={'value': 'new'}))
    target = forms.CharField(widget=forms.HiddenInput(attrs={'value': 'ticket'}))

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


class EditTicketForm(NewTicketForm):
    action = forms.CharField(widget=forms.HiddenInput(attrs={'value': 'edit'}))