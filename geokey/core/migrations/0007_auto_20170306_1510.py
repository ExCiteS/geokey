# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_loggerhistory_media_file'),
    ]

    operations = [
        migrations.RenameField(
            model_name='loggerhistory',
            old_name='media_file',
            new_name='mediafile',
        ),
    ]
