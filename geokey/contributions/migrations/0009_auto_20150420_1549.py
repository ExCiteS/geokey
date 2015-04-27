# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0008_auto_20150312_1508'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalobservation',
            options={'ordering': ('-history_date', '-history_id'), 'get_latest_by': 'history_date', 'verbose_name': 'historical observation'},
        ),
        migrations.AlterField(
            model_name='historicalobservation',
            name='history_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
