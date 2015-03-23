# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0002_auto_20150112_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='skip_authorization',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='application',
            name='user',
            field=models.ForeignKey(related_name='applications_application', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
