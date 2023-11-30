from django import forms

from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            'name', 'event_type', 'is_online', 
            'datetime_start', 'datetime_end', 'place',
            'description'
        )
