# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0009_auto_20150130_1440'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name']},
        ),
    ]
