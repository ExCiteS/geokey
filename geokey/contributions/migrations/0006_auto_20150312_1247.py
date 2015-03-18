# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0005_auto_20150202_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalobservation',
            name='properties',
            field=django_pgjson.fields.JsonBField(default={}),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='properties',
            field=django_pgjson.fields.JsonBField(default={}),
            preserve_default=True,
        ),
    ]
