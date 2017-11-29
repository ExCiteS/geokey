# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0002_auto_20150112_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='user',
            field=models.ForeignKey(related_name='applications_application', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
