# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20150123_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='everyone_contributes',
            field=models.CharField(default=b'auth', max_length=20, choices=[(b'true', b'true'), (b'auth', b'auth'), (b'false', b'false')]),
            preserve_default=True,
        ),
    ]
