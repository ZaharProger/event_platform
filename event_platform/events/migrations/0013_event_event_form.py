# Generated by Django 5.0 on 2024-04-17 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_event_event_character_event_event_level_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_form',
            field=models.CharField(default='', max_length=150),
        ),
    ]
