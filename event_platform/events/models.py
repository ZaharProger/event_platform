from django.db import models

from docs.models import Doc, DocField
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
    docs = models.ManyToManyField(Doc, through='EventDoc')


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


class Task(models.Model):
    class TaskStates(models.TextChoices):
        NOT_ASSIGNED = 'Не назначена',
        ACTIVE = 'В исполнении'
        COMPLETED = 'Завершена'

    event = models.ForeignKey(
        to=Event, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='task_event'
    )
    field = models.OneToOneField(
        to=DocField, 
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    parent = models.ForeignKey(
        to='self', 
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    datetime_start = models.BigIntegerField(default=0)
    datetime_end = models.BigIntegerField(blank=True, null=True)
    state = models.CharField(
        default=TaskStates.NOT_ASSIGNED,
        max_length=50,
        choices=TaskStates.choices
    )
    users = models.ManyToManyField(UserProfile, through='UserTask')


class UserTask(models.Model):
    user = models.ForeignKey(
        to=UserProfile, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    task = models.ForeignKey(
        to=Task, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    is_responsible = models.BooleanField(default=False)
