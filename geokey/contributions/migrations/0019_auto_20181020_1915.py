# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0018_historicalcomment'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentFile',
            fields=[
                ('mediafile_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.MediaFile')),
                ('document', models.FileField(upload_to=b'user-uploads/documents')),
                ('thumbnail', models.ImageField(null=True, upload_to=b'user-uploads/documents')),
            ],
            options={
                'ordering': ['id'],
            },
            bases=('contributions.mediafile',),
        ),
        migrations.AlterModelOptions(
            name='mediafile',
            options={},
        ),
    ]
