# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150824_1603'),
        ('oauth2_provider', '0002_08_updates'),
    ]

    operations = [
        migrations.RunSQL('DROP TABLE IF EXISTS oauth2_provider_application;')
    ]
