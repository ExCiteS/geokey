# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserGroup'
        db.create_table(u'backend_usergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('backend', ['UserGroup'])

        # Adding M2M table for field users on 'UserGroup'
        m2m_table_name = db.shorten_name(u'backend_usergroup_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('usergroup', models.ForeignKey(orm['backend.usergroup'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['usergroup_id', 'user_id'])

        # Adding model 'Project'
        db.create_table(u'backend_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('isprivate', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('everyonecontributes', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('admins', self.gf('django.db.models.fields.related.OneToOneField')(related_name='admingroup', unique=True, to=orm['backend.UserGroup'])),
            ('contributors', self.gf('django.db.models.fields.related.OneToOneField')(related_name='contributorgroup', unique=True, to=orm['backend.UserGroup'])),
        ))
        db.send_create_signal('backend', ['Project'])

        # Adding model 'FeatureType'
        db.create_table(u'backend_featuretype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backend.Project'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('backend', ['FeatureType'])

        # Adding model 'Field'
        db.create_table(u'backend_field', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('featuretype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backend.FeatureType'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('backend', ['Field'])

        # Adding model 'TextField'
        db.create_table(u'backend_textfield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['backend.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('backend', ['TextField'])

        # Adding model 'NumericField'
        db.create_table(u'backend_numericfield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['backend.Field'], unique=True, primary_key=True)),
            ('minval', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('maxval', self.gf('django.db.models.fields.FloatField')(null=True)),
        ))
        db.send_create_signal('backend', ['NumericField'])

        # Adding model 'TrueFalseField'
        db.create_table(u'backend_truefalsefield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['backend.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('backend', ['TrueFalseField'])

        # Adding model 'DateTimeField'
        db.create_table(u'backend_datetimefield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['backend.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('backend', ['DateTimeField'])

        # Adding model 'LookupField'
        db.create_table(u'backend_lookupfield', (
            (u'field_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['backend.Field'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('backend', ['LookupField'])

        # Adding model 'LookupValue'
        db.create_table(u'backend_lookupvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backend.LookupField'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('backend', ['LookupValue'])

        # Adding model 'View'
        db.create_table(u'backend_view', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backend.Project'])),
        ))
        db.send_create_signal('backend', ['View'])

        # Adding model 'ViewGroup'
        db.create_table(u'backend_viewgroup', (
            (u'usergroup_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['backend.UserGroup'], unique=True, primary_key=True)),
            ('can_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('can_read', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('can_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('view', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backend.View'])),
        ))
        db.send_create_signal('backend', ['ViewGroup'])

        # Adding model 'Feature'
        db.create_table(u'backend_feature', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('geometry', self.gf('django.contrib.gis.db.models.fields.GeometryField')(geography=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('featuretype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backend.FeatureType'])),
        ))
        db.send_create_signal('backend', ['Feature'])

        # Adding M2M table for field projects on 'Feature'
        m2m_table_name = db.shorten_name(u'backend_feature_projects')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feature', models.ForeignKey(orm['backend.feature'], null=False)),
            ('project', models.ForeignKey(orm['backend.project'], null=False))
        ))
        db.create_unique(m2m_table_name, ['feature_id', 'project_id'])

        # Adding model 'Observation'
        db.create_table(u'backend_observation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('djorm_hstore.fields.DictionaryField')(db_index=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('feature', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backend.Feature'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('backend', ['Observation'])

        # Adding model 'FeatureComment'
        db.create_table(u'backend_featurecomment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('commentto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backend.Feature'])),
            ('respondsto', self.gf('django.db.models.fields.related.ForeignKey')(related_name='respondsto_set', null=True, to=orm['backend.FeatureComment'])),
        ))
        db.send_create_signal('backend', ['FeatureComment'])

        # Adding model 'ObservationComment'
        db.create_table(u'backend_observationcomment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('commentto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['backend.Observation'])),
            ('respondsto', self.gf('django.db.models.fields.related.ForeignKey')(related_name='respondsto_set', null=True, to=orm['backend.ObservationComment'])),
        ))
        db.send_create_signal('backend', ['ObservationComment'])


    def backwards(self, orm):
        # Deleting model 'UserGroup'
        db.delete_table(u'backend_usergroup')

        # Removing M2M table for field users on 'UserGroup'
        db.delete_table(db.shorten_name(u'backend_usergroup_users'))

        # Deleting model 'Project'
        db.delete_table(u'backend_project')

        # Deleting model 'FeatureType'
        db.delete_table(u'backend_featuretype')

        # Deleting model 'Field'
        db.delete_table(u'backend_field')

        # Deleting model 'TextField'
        db.delete_table(u'backend_textfield')

        # Deleting model 'NumericField'
        db.delete_table(u'backend_numericfield')

        # Deleting model 'TrueFalseField'
        db.delete_table(u'backend_truefalsefield')

        # Deleting model 'DateTimeField'
        db.delete_table(u'backend_datetimefield')

        # Deleting model 'LookupField'
        db.delete_table(u'backend_lookupfield')

        # Deleting model 'LookupValue'
        db.delete_table(u'backend_lookupvalue')

        # Deleting model 'View'
        db.delete_table(u'backend_view')

        # Deleting model 'ViewGroup'
        db.delete_table(u'backend_viewgroup')

        # Deleting model 'Feature'
        db.delete_table(u'backend_feature')

        # Removing M2M table for field projects on 'Feature'
        db.delete_table(db.shorten_name(u'backend_feature_projects'))

        # Deleting model 'Observation'
        db.delete_table(u'backend_observation')

        # Deleting model 'FeatureComment'
        db.delete_table(u'backend_featurecomment')

        # Deleting model 'ObservationComment'
        db.delete_table(u'backend_observationcomment')


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
        'backend.datetimefield': {
            'Meta': {'object_name': 'DateTimeField', '_ormbases': ['backend.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['backend.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        'backend.feature': {
            'Meta': {'object_name': 'Feature'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'featuretype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['backend.FeatureType']"}),
            'geometry': ('django.contrib.gis.db.models.fields.GeometryField', [], {'geography': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['backend.Project']", 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'backend.featurecomment': {
            'Meta': {'object_name': 'FeatureComment'},
            'commentto': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['backend.Feature']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'respondsto': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'respondsto_set'", 'null': 'True', 'to': "orm['backend.FeatureComment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'backend.featuretype': {
            'Meta': {'object_name': 'FeatureType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['backend.Project']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'backend.field': {
            'Meta': {'object_name': 'Field'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'featuretype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['backend.FeatureType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'backend.lookupfield': {
            'Meta': {'object_name': 'LookupField', '_ormbases': ['backend.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['backend.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        'backend.lookupvalue': {
            'Meta': {'object_name': 'LookupValue'},
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['backend.LookupField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'backend.numericfield': {
            'Meta': {'object_name': 'NumericField', '_ormbases': ['backend.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['backend.Field']", 'unique': 'True', 'primary_key': 'True'}),
            'maxval': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'minval': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        'backend.observation': {
            'Meta': {'object_name': 'Observation'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'data': ('djorm_hstore.fields.DictionaryField', [], {'db_index': 'True'}),
            'feature': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['backend.Feature']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'backend.observationcomment': {
            'Meta': {'object_name': 'ObservationComment'},
            'commentto': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['backend.Observation']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'respondsto': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'respondsto_set'", 'null': 'True', 'to': "orm['backend.ObservationComment']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'backend.project': {
            'Meta': {'object_name': 'Project'},
            'admins': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'admingroup'", 'unique': 'True', 'to': "orm['backend.UserGroup']"}),
            'contributors': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'contributorgroup'", 'unique': 'True', 'to': "orm['backend.UserGroup']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'everyonecontributes': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isprivate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'backend.textfield': {
            'Meta': {'object_name': 'TextField', '_ormbases': ['backend.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['backend.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        'backend.truefalsefield': {
            'Meta': {'object_name': 'TrueFalseField', '_ormbases': ['backend.Field']},
            u'field_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['backend.Field']", 'unique': 'True', 'primary_key': 'True'})
        },
        'backend.usergroup': {
            'Meta': {'object_name': 'UserGroup'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'})
        },
        'backend.view': {
            'Meta': {'object_name': 'View'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['backend.Project']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'backend.viewgroup': {
            'Meta': {'object_name': 'ViewGroup', '_ormbases': ['backend.UserGroup']},
            'can_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'usergroup_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['backend.UserGroup']", 'unique': 'True', 'primary_key': 'True'}),
            'view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['backend.View']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['backend']