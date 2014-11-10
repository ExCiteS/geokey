# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'categories_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='categories', to=orm['projects.Project'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=20)),
            ('default_status', self.gf('django.db.models.fields.CharField')(default='pending', max_length=20)),
            ('colour', self.gf('django.db.models.fields.TextField')(default='#0033ff')),
            ('symbol', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
        ))
        db.send_create_signal(u'categories', ['Category'])

        # Adding model 'Field'
        db.create_table(u'categories_field', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['categories.Category'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=20)),
        ))
        db.send_create_signal(u'categories', ['Field'])

        # Adding unique constraint on 'Field', fields ['key', 'category']
        db.create_unique(u'categories_field', ['key', 'category_id'])

        # Adding model 'TextField'
        db.create_table(u'categories_textfield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['categories.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'categories', ['TextField'])

        # Adding model 'NumericField'
        db.create_table(u'categories_numericfield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['categories.Field'], unique=True, primary_key=True)),
            ('minval', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('maxval', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'categories', ['NumericField'])

        # Adding model 'TrueFalseField'
        db.create_table(u'categories_truefalsefield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['categories.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'categories', ['TrueFalseField'])

        # Adding model 'DateTimeField'
        db.create_table(u'categories_datetimefield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['categories.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'categories', ['DateTimeField'])

        # Adding model 'LookupField'
        db.create_table(u'categories_lookupfield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['categories.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'categories', ['LookupField'])

        # Adding model 'LookupValue'
        db.create_table(u'categories_lookupvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='lookupvalues', to=orm['categories.LookupField'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=20)),
        ))
        db.send_create_signal(u'categories', ['LookupValue'])

        # Adding model 'MultipleLookupField'
        db.create_table(u'categories_multiplelookupfield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['categories.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'categories', ['MultipleLookupField'])

        # Adding model 'MultipleLookupValue'
        db.create_table(u'categories_multiplelookupvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='lookupvalues', to=orm['categories.MultipleLookupField'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=20)),
        ))
        db.send_create_signal(u'categories', ['MultipleLookupValue'])


    def backwards(self, orm):
        # Removing unique constraint on 'Field', fields ['key', 'category']
        db.delete_unique(u'categories_field', ['key', 'category_id'])

        # Deleting model 'Category'
        db.delete_table(u'categories_category')

        # Deleting model 'Field'
        db.delete_table(u'categories_field')

        # Deleting model 'TextField'
        db.delete_table(u'categories_textfield')

        # Deleting model 'NumericField'
        db.delete_table(u'categories_numericfield')

        # Deleting model 'TrueFalseField'
        db.delete_table(u'categories_truefalsefield')

        # Deleting model 'DateTimeField'
        db.delete_table(u'categories_datetimefield')

        # Deleting model 'LookupField'
        db.delete_table(u'categories_lookupfield')

        # Deleting model 'LookupValue'
        db.delete_table(u'categories_lookupvalue')

        # Deleting model 'MultipleLookupField'
        db.delete_table(u'categories_multiplelookupfield')

        # Deleting model 'MultipleLookupValue'
        db.delete_table(u'categories_multiplelookupvalue')


    models = {
        u'categories.category': {
            'Meta': {'object_name': 'Category'},
            'colour': ('django.db.models.fields.TextField', [], {'default': "'#0033ff'"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'default_status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '20'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'categories'", 'to': u"orm['projects.Project']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'symbol': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'})
        },
        u'categories.datetimefield': {
            'Meta': {'object_name': 'DateTimeField', '_ormbases': [u'categories.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['categories.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'categories.field': {
            'Meta': {'unique_together': "(('key', 'category'),)", 'object_name': 'Field'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': u"orm['categories.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
        },
        u'categories.lookupfield': {
            'Meta': {'object_name': 'LookupField', '_ormbases': [u'categories.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['categories.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'categories.lookupvalue': {
            'Meta': {'object_name': 'LookupValue'},
            'field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lookupvalues'", 'to': u"orm['categories.LookupField']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
        },
        u'categories.multiplelookupfield': {
            'Meta': {'object_name': 'MultipleLookupField', '_ormbases': [u'categories.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['categories.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'categories.multiplelookupvalue': {
            'Meta': {'object_name': 'MultipleLookupValue'},
            'field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lookupvalues'", 'to': u"orm['categories.MultipleLookupField']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
        },
        u'categories.numericfield': {
            'Meta': {'object_name': 'NumericField', '_ormbases': [u'categories.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['categories.Field']", 'unique': 'True', 'primary_key': 'True'}),
            'maxval': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'minval': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'categories.textfield': {
            'Meta': {'object_name': 'TextField', '_ormbases': [u'categories.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['categories.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'categories.truefalsefield': {
            'Meta': {'object_name': 'TrueFalseField', '_ormbases': [u'categories.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['categories.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'projects.admins': {
            'Meta': {'ordering': "['project__name']", 'unique_together': "(('project', 'user'),)", 'object_name': 'Admins'},
            'contact': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admin_of'", 'to': u"orm['projects.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'has_admins'", 'to': u"orm['users.User']"})
        },
        u'projects.project': {
            'Meta': {'ordering': "['name']", 'object_name': 'Project'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'admins'", 'symmetrical': 'False', 'through': u"orm['projects.Admins']", 'to': u"orm['users.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'everyone_contributes': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'geographic_extend': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'geography': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isprivate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
        },
        u'users.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'display_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['categories']