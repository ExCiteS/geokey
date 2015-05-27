# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def clean_youtube_links(apps, schema_editor):
    VideoFile = apps.get_model("contributions", "VideoFile")

    for file in VideoFile.objects.all():
        new_link = file.youtube_link.replace('http://', 'https://')
        file.youtube_link = new_link
        file.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0010_auto_20150511_1132'),
    ]

    operations = [
        migrations.RunPython(clean_youtube_links),
    ]
