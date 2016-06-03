# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0016_multiplelookupvalue_symbol'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='expiry_field',
            field=models.ForeignKey(related_name='expiry_field_of', to='categories.Field', null=True),
        ),
    ]
