# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datagroupings', '0002_auto_20150106_1338'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='grouping',
            options={'ordering': ['name']},
        ),
    ]
