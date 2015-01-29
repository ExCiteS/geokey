# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0002_auto_20150106_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalobservation',
            name='display_field',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='display_field',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
