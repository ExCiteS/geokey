# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('provider', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('download_url', models.URLField()),
                ('redirect_url', models.URLField()),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'deleted', b'deleted')])),
                ('client', models.ForeignKey(related_name='app', to='provider.Client', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
