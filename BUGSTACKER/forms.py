from django import forms
from .models import Ticket


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
