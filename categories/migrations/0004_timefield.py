# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0003_datefield'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeField',
            fields=[
                ('field_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='categories.Field')),
            ],
            options={
            },
            bases=('categories.field',),
        ),
    ]
