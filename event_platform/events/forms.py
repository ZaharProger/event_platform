from django import forms

from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            'name', 'event_form', 'event_type',
            'event_level', 'event_character', 'is_online', 'for_students', 
            'datetime_start', 'datetime_end', 'place',
            'description'
        )
