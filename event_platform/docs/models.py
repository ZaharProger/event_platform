from django.db import models


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


class DocField(models.Model):
    doc = models.ForeignKey(
        to=Doc, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='doc_field'
    )
    name = models.CharField(default='', max_length=50)


class FieldValue(models.Model):
    field = models.ForeignKey(
        to=DocField,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='field_value'
    )
    value = models.CharField(default='', max_length=300)
