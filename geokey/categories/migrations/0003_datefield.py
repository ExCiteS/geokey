# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_auto_20150106_1338'),
    ]

    operations = [
        migrations.CreateModel(
            name='DateField',
            fields=[
                ('field_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='categories.Field')),
            ],
            options={
            },
            bases=('categories.field',),
        ),
    ]
