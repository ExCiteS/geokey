# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0016_audiofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalobservation',
            name='expiry_field',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='observation',
            name='expiry_field',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
