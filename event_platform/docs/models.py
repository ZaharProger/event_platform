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

    class FieldTypes(models.TextChoices):
        TEXT = 'текст'
        DATE = 'дата'

    doc = models.ForeignKey(
        to=Doc, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='fields'
    )
    name = models.CharField(default='', max_length=150)
    field_type = models.CharField(
        default=FieldTypes.TEXT,
        max_length=20,
        choices=FieldTypes.choices
    )


class FieldValue(models.Model):
    field = models.ForeignKey(
        to=DocField,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='values'
    )
    value = models.CharField(default='', max_length=300)
