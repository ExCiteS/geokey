# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20150123_1507'),
    ]

    operations = [
        migrations.RunSQL("DELETE FROM projects_admins WHERE project_id IN (SELECT id FROM projects_project WHERE status = 'deleted');")
    ]
