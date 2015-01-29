# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_hstore.fields
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'deleted', b'deleted')])),
                ('review_status', models.CharField(blank=True, max_length=10, null=True, choices=[(b'open', b'open'), (b'resolved', b'resolved')])),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoricalObservation',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('location_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('project_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('category_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'draft', b'draft'), (b'review', b'review'), (b'pending', b'pending'), (b'deleted', b'deleted')])),
                ('attributes', django_hstore.fields.DictionaryField(db_index=True)),
                ('created_at', models.DateTimeField(editable=False, blank=True)),
                ('creator_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('updated_at', models.DateTimeField(null=True, editable=False, blank=True)),
                ('updator_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('version', models.IntegerField(default=1)),
                ('search_matches', models.TextField()),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical observation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(srid=4326, geography=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('version', models.IntegerField(default=1)),
                ('private', models.BooleanField(default=False)),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'review', b'review')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MediaFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'deleted', b'deleted')])),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImageFile',
            fields=[
                ('mediafile_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.MediaFile')),
                ('image', models.ImageField(upload_to=b'user-uploads/images')),
            ],
            options={
                'ordering': ['id'],
            },
            bases=('contributions.mediafile',),
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'draft', b'draft'), (b'review', b'review'), (b'pending', b'pending'), (b'deleted', b'deleted')])),
                ('attributes', django_hstore.fields.DictionaryField(db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('version', models.IntegerField(default=1)),
                ('search_matches', models.TextField()),
                ('category', models.ForeignKey(to='categories.Category')),
            ],
            options={
                'ordering': ['-updated_at', 'id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VideoFile',
            fields=[
                ('mediafile_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='contributions.MediaFile')),
                ('video', models.ImageField(upload_to=b'user-uploads/videos')),
                ('youtube_id', models.CharField(max_length=100)),
                ('thumbnail', models.ImageField(null=True, upload_to=b'user-uploads/videos')),
                ('youtube_link', models.URLField(max_length=255, null=True, blank=True)),
                ('swf_link', models.URLField(max_length=255, null=True, blank=True)),
            ],
            options={
                'ordering': ['id'],
            },
            bases=('contributions.mediafile',),
        ),
    ]
