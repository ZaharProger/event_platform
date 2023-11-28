from django.db import models

from docs.models import Doc
from users.models import UserProfile

class Event(models.Model):

    class EventTypes(models.TextChoices):
        INDIVIDUAL = 'С индивидуальным участием'
        TEAM = 'Командное участие'

    name = models.CharField(default='', max_length=50)
    event_type = models.CharField(
        default=EventTypes.INDIVIDUAL, 
        max_length=100, 
        choices=EventTypes.choices
    )
    is_online = models.BooleanField(default=False)
    place = models.CharField(default='', max_length=150)
    datetime_start = models.BigIntegerField(default=0)
    datetime_end = models.BigIntegerField(blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    organizer = models.ForeignKey(
        to=UserProfile, 
        on_delete=models.CASCADE,
        null=True, 
        blank=True
    )
    is_complete = models.BooleanField(default=False)
    secret_code = models.CharField(max_length=8, blank=True, null=True)
    docs = models.ManyToManyField(Doc, through='EventDoc')


class EventDoc(models.Model):
    event = models.ForeignKey(
        to=Event, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    doc = models.ForeignKey(
        to=Doc, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    name = models.CharField(default='', max_length=50)