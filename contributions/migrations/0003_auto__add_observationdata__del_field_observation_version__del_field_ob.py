# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ObservationData'
        db.create_table(u'contributions_observationdata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('attributes', self.gf(u'django_hstore.fields.DictionaryField')(db_index=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('observation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='data', to=orm['contributions.Observation'])),
        ))
        db.send_create_signal(u'contributions', ['ObservationData'])

        # Deleting field 'Observation.version'
        db.delete_column(u'contributions_observation', 'version')

        # Deleting field 'Observation.creator'
        db.delete_column(u'contributions_observation', 'creator_id')

        # Deleting field 'Observation.created_at'
        db.delete_column(u'contributions_observation', 'created_at')

        # Deleting field 'Observation.data'
        db.delete_column(u'contributions_observation', 'data')


        # Changing field 'Location.description'
        db.alter_column(u'contributions_location', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Location.name'
        db.alter_column(u'contributions_location', 'name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

    def backwards(self, orm):
        # Deleting model 'ObservationData'
        db.delete_table(u'contributions_observationdata')

        # Adding field 'Observation.version'
        db.add_column(u'contributions_observation', 'version',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Observation.creator'
        raise RuntimeError("Cannot reverse this migration. 'Observation.creator' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Observation.creator'
        db.add_column(u'contributions_observation', 'creator',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Observation.created_at'
        raise RuntimeError("Cannot reverse this migration. 'Observation.created_at' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Observation.created_at'
        db.add_column(u'contributions_observation', 'created_at',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Observation.data'
        raise RuntimeError("Cannot reverse this migration. 'Observation.data' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Observation.data'
        db.add_column(u'contributions_observation', 'data',
                      self.gf(u'django_hstore.fields.DictionaryField')(db_index=True),
                      keep_default=False)


        # Changing field 'Location.description'
        db.alter_column(u'contributions_location', 'description', self.gf('django.db.models.fields.TextField')(default=None))

        # Changing field 'Location.name'
        db.alter_column(u'contributions_location', 'name', self.gf('django.db.models.fields.CharField')(default=None, max_length=100))

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
        u'contributions.comment': {
            'Meta': {'object_name': 'Comment'},
            'commentto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contributions.Observation']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'respondsto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contributions.Comment']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'contributions.location': {
            'Meta': {'object_name': 'Location'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.GeometryField', [], {'geography': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'private_for_project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']", 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'contributions.observation': {
            'Meta': {'object_name': 'Observation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'observations'", 'to': u"orm['contributions.Location']"}),
            'observationtype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['observationtypes.ObservationType']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'observations'", 'to': u"orm['projects.Project']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
        },
        u'contributions.observationdata': {
            'Meta': {'object_name': 'ObservationData'},
            'attributes': (u'django_hstore.fields.DictionaryField', [], {'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'data'", 'to': u"orm['contributions.Observation']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'observationtypes.observationtype': {
            'Meta': {'object_name': 'ObservationType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'observationtypes'", 'to': u"orm['projects.Project']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
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

    complete_apps = ['contributions']