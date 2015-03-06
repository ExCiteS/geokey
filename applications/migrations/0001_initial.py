# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL('DROP TABLE IF EXISTS applications_application CASCADE;'),
        migrations.RunSQL("DELETE FROM django_migrations WHERE app = 'applications';")
    ]
