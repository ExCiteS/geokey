# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ObservationType'
        db.create_table(u'observationtypes_observationtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=20)),
        ))
        db.send_create_signal(u'observationtypes', ['ObservationType'])

        # Adding model 'Field'
        db.create_table(u'observationtypes_field', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('featuretype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['observationtypes.ObservationType'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=20)),
        ))
        db.send_create_signal(u'observationtypes', ['Field'])

        # Adding model 'TextField'
        db.create_table(u'observationtypes_textfield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['observationtypes.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'observationtypes', ['TextField'])

        # Adding model 'NumericField'
        db.create_table(u'observationtypes_numericfield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['observationtypes.Field'], unique=True, primary_key=True)),
            ('minval', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('maxval', self.gf('django.db.models.fields.FloatField')(null=True)),
        ))
        db.send_create_signal(u'observationtypes', ['NumericField'])

        # Adding model 'TrueFalseField'
        db.create_table(u'observationtypes_truefalsefield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['observationtypes.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'observationtypes', ['TrueFalseField'])

        # Adding model 'DateTimeField'
        db.create_table(u'observationtypes_datetimefield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['observationtypes.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'observationtypes', ['DateTimeField'])

        # Adding model 'LookupField'
        db.create_table(u'observationtypes_lookupfield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['observationtypes.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'observationtypes', ['LookupField'])

        # Adding model 'LookupValue'
        db.create_table(u'observationtypes_lookupvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['observationtypes.LookupField'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default='active')),
        ))
        db.send_create_signal(u'observationtypes', ['LookupValue'])


    def backwards(self, orm):
        # Deleting model 'ObservationType'
        db.delete_table(u'observationtypes_observationtype')

        # Deleting model 'Field'
        db.delete_table(u'observationtypes_field')

        # Deleting model 'TextField'
        db.delete_table(u'observationtypes_textfield')

        # Deleting model 'NumericField'
        db.delete_table(u'observationtypes_numericfield')

        # Deleting model 'TrueFalseField'
        db.delete_table(u'observationtypes_truefalsefield')

        # Deleting model 'DateTimeField'
        db.delete_table(u'observationtypes_datetimefield')

        # Deleting model 'LookupField'
        db.delete_table(u'observationtypes_lookupfield')

        # Deleting model 'LookupValue'
        db.delete_table(u'observationtypes_lookupvalue')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'observationtypes.datetimefield': {
            'Meta': {'object_name': 'DateTimeField', '_ormbases': [u'observationtypes.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['observationtypes.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'observationtypes.field': {
            'Meta': {'object_name': 'Field'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'featuretype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['observationtypes.ObservationType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
        },
        u'observationtypes.lookupfield': {
            'Meta': {'object_name': 'LookupField', '_ormbases': [u'observationtypes.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['observationtypes.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'observationtypes.lookupvalue': {
            'Meta': {'object_name': 'LookupValue'},
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['observationtypes.LookupField']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': "'active'"})
        },
        u'observationtypes.numericfield': {
            'Meta': {'object_name': 'NumericField', '_ormbases': [u'observationtypes.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['observationtypes.Field']", 'unique': 'True', 'primary_key': 'True'}),
            'maxval': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'minval': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        u'observationtypes.observationtype': {
            'Meta': {'object_name': 'ObservationType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']"}),
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
            'admins': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'admingroup'", 'unique': 'True', 'to': u"orm['projects.UserGroup']"}),
            'contributors': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'contributorgroup'", 'unique': 'True', 'to': u"orm['projects.UserGroup']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'everyonecontributes': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isprivate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
        },
        u'projects.usergroup': {
            'Meta': {'object_name': 'UserGroup'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['observationtypes']