# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'inactive', b'inactive'), (b'deleted', b'deleted')])),
                ('default_status', models.CharField(default=b'pending', max_length=20, choices=[(b'active', b'active'), (b'pending', b'pending')])),
                ('colour', models.TextField(default=b'#0033ff')),
                ('symbol', models.ImageField(null=True, upload_to=b'symbols')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('key', models.CharField(max_length=103)),
                ('description', models.TextField(null=True, blank=True)),
                ('required', models.BooleanField(default=False)),
                ('order', models.IntegerField(default=0)),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'inactive', b'inactive'), (b'deleted', b'deleted')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DateTimeField',
            fields=[
                ('field_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='categories.Field')),
            ],
            options={
            },
            bases=('categories.field',),
        ),
        migrations.CreateModel(
            name='LookupField',
            fields=[
                ('field_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='categories.Field')),
            ],
            options={
            },
            bases=('categories.field',),
        ),
        migrations.CreateModel(
            name='LookupValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'inactive', b'inactive'), (b'deleted', b'deleted')])),
                ('field', models.ForeignKey(related_name='lookupvalues', to='categories.LookupField')),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MultipleLookupField',
            fields=[
                ('field_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='categories.Field')),
            ],
            options={
            },
            bases=('categories.field',),
        ),
        migrations.CreateModel(
            name='MultipleLookupValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('status', models.CharField(default=b'active', max_length=20, choices=[(b'active', b'active'), (b'inactive', b'inactive'), (b'deleted', b'deleted')])),
                ('field', models.ForeignKey(related_name='lookupvalues', to='categories.MultipleLookupField')),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NumericField',
            fields=[
                ('field_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='categories.Field')),
                ('minval', models.FloatField(null=True, blank=True)),
                ('maxval', models.FloatField(null=True, blank=True)),
            ],
            options={
            },
            bases=('categories.field',),
        ),
        migrations.CreateModel(
            name='TextField',
            fields=[
                ('field_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='categories.Field')),
            ],
            options={
            },
            bases=('categories.field',),
        ),
        migrations.AddField(
            model_name='field',
            name='category',
            field=models.ForeignKey(related_name='fields', to='categories.Category'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='field',
            unique_together=set([('key', 'category')]),
        ),
    ]
