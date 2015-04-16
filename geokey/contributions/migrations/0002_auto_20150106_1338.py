# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='creator',
            field=models.ForeignKey(related_name='creator', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='location',
            field=models.ForeignKey(related_name='locations', to='contributions.Location'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='project',
            field=models.ForeignKey(related_name='observations', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='updator',
            field=models.ForeignKey(related_name='updator', to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mediafile',
            name='contribution',
            field=models.ForeignKey(related_name='files_attached', to='contributions.Observation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mediafile',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='location',
            name='private_for_project',
            field=models.ForeignKey(to='projects.Project', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='historicalobservation',
            name='history_user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='commentto',
            field=models.ForeignKey(related_name='comments', to='contributions.Observation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='respondsto',
            field=models.ForeignKey(related_name='responses', blank=True, to='contributions.Comment', null=True),
            preserve_default=True,
        ),
    ]
