# Generated by Django 4.2.7 on 2023-12-05 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docs', '0005_alter_doc_event_alter_docfield_doc_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doc',
            name='name',
            field=models.CharField(default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='docfield',
            name='name',
            field=models.CharField(default='', max_length=150),
        ),
    ]
