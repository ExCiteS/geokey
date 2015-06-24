# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields
import django.utils.timezone
from django.conf import settings


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# geokey.users.migrations.0002_auto_20150106_1420

def create_anonymous(apps, schema_editor):
    User = apps.get_model("users", "User")
    if not User.objects.filter(display_name='AnonymousUser').exists():
        User.objects.create(
            display_name='AnonymousUser',
            password='',
            email=''
        )


class Migration(migrations.Migration):

    replaces = [(b'users', '0001_initial'), (b'users', '0002_auto_20150106_1420'), (b'users', '0003_auto_20150611_1307'), (b'users', '0004_auto_20150617_0902')]

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('email', models.EmailField(unique=True, max_length=75)),
                ('display_name', models.CharField(unique=True, max_length=50)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('can_contribute', models.BooleanField(default=True)),
                ('can_moderate', models.BooleanField(default=False)),
                ('project', models.ForeignKey(related_name='usergroups', to='projects.Project')),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='usergroup',
            name='filters',
            field=django_pgjson.fields.JsonBField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='usergroup',
            name='where_clause',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.RunPython(create_anonymous),
    ]
