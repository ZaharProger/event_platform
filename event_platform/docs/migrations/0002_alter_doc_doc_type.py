# Generated by Django 4.2.7 on 2023-12-04 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doc',
            name='doc_type',
            field=models.CharField(choices=[('Дорожная карта', 'Roadmap'), ('Программа мероприятия', 'Programme'), ('Проект сметы', 'Money'), ('Служебная записка', 'Note'), ('Приказ', 'Order'), ('Отчет', 'Report')], default='Программа мероприятия', max_length=50),
        ),
    ]
