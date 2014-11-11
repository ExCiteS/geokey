# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'TrueFalseField'
        db.delete_table(u'categories_truefalsefield')


    def backwards(self, orm):
        # Adding model 'TrueFalseField'
        db.create_table(u'categories_truefalsefield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['categories.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'categories', ['TrueFalseField'])


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