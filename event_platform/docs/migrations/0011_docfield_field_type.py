# Generated by Django 5.0 on 2024-01-23 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0010_remove_usertask_task_remove_usertask_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='docfield',
            name='field_type',
            field=models.CharField(choices=[('текст', 'Text'), ('дата', 'Date')], default='текст', max_length=20),
        ),
    ]