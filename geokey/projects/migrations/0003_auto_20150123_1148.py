# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20150106_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='everyone_contributes',
            field=models.CharField(default=b'Auth', max_length=20, choices=[(b'True', b'True'), (b'Auth', b'Auth'), (b'False', b'False')]),
            preserve_default=True,
        ),
    ]
