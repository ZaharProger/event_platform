# Generated by Django 5.0 on 2024-04-17 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0011_alter_event_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_character',
            field=models.CharField(choices=[('Учебный', 'Study'), ('Научный', 'Scientific'), ('Научно-практический', 'Scientific Practical'), ('Научно-методический', 'Scientific Metodological'), ('Научно-технический', 'Scientific Technical')], default='Учебный', max_length=100),
        ),
        migrations.AddField(
            model_name='event',
            name='event_level',
            field=models.CharField(choices=[('Внутривузовский', 'Internal'), ('Межвузовский', 'Interuniversity'), ('Региональный', 'Regional'), ('Всероссийский', 'Country'), ('Международный', 'International')], default='Внутривузовский', max_length=100),
        ),
        migrations.AddField(
            model_name='event',
            name='for_students',
            field=models.BooleanField(default=False),
        ),
    ]