# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0015_auto_20150907_1345'),
    ]

    operations = [
        migrations.CreateModel(
            name='AudioFile',
            fields=[
                ('mediafile_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.MediaFile')),
                ('audio', models.FileField(upload_to=b'user-uploads/audio')),
            ],
            options={
                'ordering': ['id'],
            },
            bases=('contributions.mediafile',),
        ),
    ]
