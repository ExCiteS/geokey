# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='admins',
            field=models.ManyToManyField(related_name='admins', through='projects.Admins', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='creator',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='admins',
            name='project',
            field=models.ForeignKey(related_name='admin_of', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='admins',
            name='user',
            field=models.ForeignKey(related_name='has_admins', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='admins',
            unique_together=set([('project', 'user')]),
        ),
    ]
