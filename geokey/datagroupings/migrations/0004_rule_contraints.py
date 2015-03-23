# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('datagroupings', '0003_auto_20150202_1023'),
    ]

    operations = [
        migrations.AddField(
            model_name='rule',
            name='constraints',
            field=django_pgjson.fields.JsonBField(default=None, null=True),
            preserve_default=True,
        ),
    ]
