# Generated by Django 4.2.7 on 2023-12-11 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertask',
            name='is_creator',
            field=models.BooleanField(default=False),
        ),
    ]
