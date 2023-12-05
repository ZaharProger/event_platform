# Generated by Django 4.2.7 on 2023-12-05 06:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_remove_task_event_remove_task_field_and_more'),
        ('docs', '0004_task_doc_event_doc_name_usertask_task_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doc',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='docs', to='events.event'),
        ),
        migrations.AlterField(
            model_name='docfield',
            name='doc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='docs.doc'),
        ),
        migrations.AlterField(
            model_name='fieldvalue',
            name='field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='values', to='docs.docfield'),
        ),
        migrations.AlterField(
            model_name='task',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='events.event'),
        ),
    ]
