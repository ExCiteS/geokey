# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_anonymous(apps, schema_editor):
    User = apps.get_model("users", "User")
    if not User.objects.filter(display_name='AnonymousUser').exists():
        User.objects.create(
            display_name='AnonymousUser',
            password='',
            email=''
        )


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_anonymous),
    ]
