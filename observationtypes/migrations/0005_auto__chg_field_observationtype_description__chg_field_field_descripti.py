# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'ObservationType.description'
        db.alter_column(u'observationtypes_observationtype', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Field.description'
        db.alter_column(u'observationtypes_field', 'description', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # Changing field 'ObservationType.description'
        db.alter_column(u'observationtypes_observationtype', 'description', self.gf('django.db.models.fields.TextField')(default=None))

        # Changing field 'Field.description'
        db.alter_column(u'observationtypes_field', 'description', self.gf('django.db.models.fields.TextField')(default=None))

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
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'observationtypes'", 'to': u"orm['projects.Project']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
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
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isprivate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
        },
        u'users.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['observationtypes']