# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'HistoricalObservation.conflict_version'
        db.delete_column(u'contributions_historicalobservation', 'conflict_version')

        # Adding field 'HistoricalObservation.updator_id'
        db.add_column(u'contributions_historicalobservation', u'updator_id',
                      self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Observation.conflict_version'
        db.delete_column(u'contributions_observation', 'conflict_version')

        # Adding field 'Observation.updator'
        db.add_column(u'contributions_observation', 'updator',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='updator', to=orm['auth.User']),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'HistoricalObservation.conflict_version'
        db.add_column(u'contributions_historicalobservation', 'conflict_version',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'HistoricalObservation.updator_id'
        db.delete_column(u'contributions_historicalobservation', u'updator_id')

        # Adding field 'Observation.conflict_version'
        db.add_column(u'contributions_observation', 'conflict_version',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Observation.updator'
        db.delete_column(u'contributions_observation', 'updator_id')


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
            'commentto': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': u"orm['contributions.Observation']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'respondsto': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'responses'", 'null': 'True', 'to': u"orm['contributions.Comment']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'contributions.historicalobservation': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalObservation'},
            'attributes': (u'django_hstore.fields.DictionaryField', [], {'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            u'creator_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            u'location_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'observationtype_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'project_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'review_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            u'updator_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
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
            'attributes': (u'django_hstore.fields.DictionaryField', [], {'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'creator'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'locations'", 'to': u"orm['contributions.Location']"}),
            'observationtype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['observationtypes.ObservationType']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'observations'", 'to': u"orm['projects.Project']"}),
            'review_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'updator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'updator'", 'to': u"orm['auth.User']"}),
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