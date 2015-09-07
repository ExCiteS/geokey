# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0014_auto_20150907_1345'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalobservation',
            name='search_matches',
        ),
        migrations.RemoveField(
            model_name='observation',
            name='search_matches',
        ),
    ]
