# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0011_auto_20150527_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalobservation',
            name='num_comments',
            field=models.IntegerField(default=None, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historicalobservation',
            name='num_media',
            field=models.IntegerField(default=None, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='num_comments',
            field=models.IntegerField(default=None, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='num_media',
            field=models.IntegerField(default=None, null=True),
            preserve_default=True,
        ),
    ]
