# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_auto_20150202_1041'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admins',
            name='contact',
        ),
    ]
