from django import forms

from .models import Task, UserTask


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('name', 'datetime_start', 'datetime_end', 'state')
