# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admins',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['project__name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('isprivate', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('everyone_contributes', models.BooleanField(default=True)),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'inactive', b'inactive'), (b'deleted', b'deleted')])),
                ('geographic_extend', django.contrib.gis.db.models.fields.PolygonField(srid=4326, null=True, geography=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
    ]
