# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20170302_2000'),
    ]

    operations = [
        migrations.AddField(
            model_name='loggerhistory',
            name='media_file',
            field=django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True),
        ),
    ]
