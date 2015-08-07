# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_count(apps, schema_editor):
    Observation = apps.get_model('contributions', 'Observation')

    for o in Observation.objects.all():
        o.num_media = o.files_attached.exclude(status='deleted').count()
        o.num_comments = o.comments.exclude(status='deleted').count()
        o.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0011_auto_20150527_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalobservation',
            name='num_comments',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historicalobservation',
            name='num_media',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='num_comments',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='num_media',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.RunPython(update_count)
    ]
