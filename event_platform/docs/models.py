from django.db import models

from events.models import Event
from users.models import UserProfile

class Doc(models.Model):

    class DocTypes(models.TextChoices):
        ROADMAP = 'Дорожная карта',
        PROGRAMME = 'Программа мероприятия',
        MONEY = 'Проект сметы',
        NOTE = 'Служебная записка',
        ORDER = 'Приказ',
        REPORT = 'Отчет'

    template_url = models.TextField(default='', max_length=150)
    doc_type = models.CharField(
        default=DocTypes.PROGRAMME,
        max_length=50,
        choices=DocTypes.choices
    )
    name = models.CharField(default='', max_length=150)
    event = models.ForeignKey(
        to=Event, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='docs'
    )


class DocField(models.Model):
    doc = models.ForeignKey(
        to=Doc, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='fields'
    )
    name = models.CharField(default='', max_length=150)


class FieldValue(models.Model):
    field = models.ForeignKey(
        to=DocField,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='values'
    )
    value = models.CharField(default='', max_length=300)


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
        related_name='events'
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
