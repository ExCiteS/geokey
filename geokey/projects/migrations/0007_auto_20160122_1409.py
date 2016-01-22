# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_remove_admins_contact'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='geographic_extend',
            new_name='geographic_extent',
        ),
        migrations.AddField(
            model_name='project',
            name='islocked',
            field=models.BooleanField(default=False),
        ),
    ]
