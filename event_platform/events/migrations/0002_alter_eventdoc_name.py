# Generated by Django 4.2.7 on 2023-11-27 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventdoc',
            name='name',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
