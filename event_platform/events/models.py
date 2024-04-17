from django.db import models

from users.models import UserProfile

class Event(models.Model):

    class EventTypes(models.TextChoices):
        INDIVIDUAL = 'С индивидуальным участием'
        TEAM = 'Командное участие'

    class EventLevels(models.TextChoices):
        INTERNAL = 'Внутривузовский'
        INTERUNIVERSITY = 'Межвузовский'
        REGIONAL = 'Региональный'
        COUNTRY = 'Всероссийский'
        INTERNATIONAL = 'Международный'
    
    class EventCharacters(models.TextChoices):
        STUDY = 'Учебный'
        SCIENTIFIC = 'Научный'
        SCIENTIFIC_PRACTICAL = 'Научно-практический'
        SCIENTIFIC_METODOLOGICAL = 'Научно-методический'
        SCIENTIFIC_TECHNICAL = 'Научно-технический'

    name = models.CharField(default='', max_length=150)
    event_type = models.CharField(
        default=EventTypes.INDIVIDUAL, 
        max_length=100, 
        choices=EventTypes.choices
    )
    event_level = models.CharField(
        default=EventLevels.INTERNAL, 
        max_length=100, 
        choices=EventLevels.choices
    )
    event_character = models.CharField(
        default=EventCharacters.STUDY, 
        max_length=100, 
        choices=EventCharacters.choices
    )
    is_online = models.BooleanField(default=False)
    for_students = models.BooleanField(default=False)
    event_form = models.CharField(default='', max_length=150)
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
