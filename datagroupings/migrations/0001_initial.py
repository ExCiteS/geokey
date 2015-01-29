# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grouping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('isprivate', models.BooleanField(default=False)),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'deleted', b'deleted')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min_date', models.DateTimeField(null=True)),
                ('max_date', models.DateTimeField(null=True)),
                ('filters', django_hstore.fields.DictionaryField(default=None, null=True, db_index=True)),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'deleted', b'deleted')])),
                ('category', models.ForeignKey(to='categories.Category')),
                ('grouping', models.ForeignKey(related_name='rules', to='datagroupings.Grouping')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
