# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import oauth2_provider.validators
import oauth2_provider.generators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL('DROP TABLE IF EXISTS applications_application CASCADE;'),
        migrations.RunSQL("DELETE FROM django_migrations WHERE app = 'applications';")
    ]
