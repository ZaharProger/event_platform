from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class UserProfile(models.Model):
    email = models.EmailField()
    phone_regex = RegexValidator(
        regex=r'^[+]{1}[0-9]{8,16}$'
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=16, 
        blank=True,
        null=True
    )
    telegram = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    organization = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    name = models.CharField(
        default='',
        max_length=30
    )


class UserPassport(User):
    user = models.OneToOneField(
        to=UserProfile, 
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
