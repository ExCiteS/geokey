# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datagroupings', '0005_auto_20150312_1741'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rule',
            name='filters',
        ),
    ]
