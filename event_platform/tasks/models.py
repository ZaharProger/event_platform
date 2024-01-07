from django.db import models

from events.models import Event
from users.models import UserProfile

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
        related_name='tasks'
    )
    parent = models.ForeignKey(
        to='self', 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    datetime_start = models.BigIntegerField(default=0)
    datetime_end = models.BigIntegerField(blank=True, null=True)
    state = models.CharField(
        default=TaskStates.NOT_ASSIGNED,
        max_length=50,
        choices=TaskStates.choices
    )
    users = models.ManyToManyField(UserProfile, through='UserTask')
    name = models.CharField(default='', max_length=150)


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
