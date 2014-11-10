# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Field.order'
        db.add_column(u'observationtypes_field', 'order',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Field.order'
        db.delete_column(u'observationtypes_field', 'order')


    models = {
        u'observationtypes.datetimefield': {
            'Meta': {'object_name': 'DateTimeField', '_ormbases': [u'observationtypes.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['observationtypes.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'observationtypes.field': {
            'Meta': {'unique_together': "(('key', 'observationtype'),)", 'object_name': 'Field'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'observationtype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': u"orm['observationtypes.ObservationType']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
        },
        u'observationtypes.lookupfield': {
            'Meta': {'object_name': 'LookupField', '_ormbases': [u'observationtypes.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['observationtypes.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'observationtypes.lookupvalue': {
            'Meta': {'object_name': 'LookupValue'},
            'field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lookupvalues'", 'to': u"orm['observationtypes.LookupField']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
        },
        u'observationtypes.numericfield': {
            'Meta': {'object_name': 'NumericField', '_ormbases': [u'observationtypes.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['observationtypes.Field']", 'unique': 'True', 'primary_key': 'True'}),
            'maxval': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'minval': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        u'observationtypes.observationtype': {
            'Meta': {'object_name': 'ObservationType'},
            'colour': ('django.db.models.fields.TextField', [], {'default': "'#0033ff'"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '20'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'observationtypes'", 'to': u"orm['projects.Project']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'symbol': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'})
        },
        u'observationtypes.textfield': {
            'Meta': {'object_name': 'TextField', '_ormbases': [u'observationtypes.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['observationtypes.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'observationtypes.truefalsefield': {
            'Meta': {'object_name': 'TrueFalseField', '_ormbases': [u'observationtypes.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['observationtypes.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'projects.project': {
            'Meta': {'object_name': 'Project'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'admins'", 'symmetrical': 'False', 'to': u"orm['users.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'everyone_contributes': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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

    complete_apps = ['observationtypes']