from django.db import models

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
    is_complete = models.BooleanField(default=False)
    secret_code = models.CharField(max_length=8, default='00000000')
    users = models.ManyToManyField(UserProfile, through='EventUser')


class EventUser(models.Model):
    event = models.ForeignKey(
        to=Event, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    user = models.ForeignKey(
        to=UserProfile, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    is_organizer = models.BooleanField(default=False)
