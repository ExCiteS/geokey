# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'users_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('display_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'users', ['User'])

        # Adding model 'UserGroup'
        db.create_table(u'users_usergroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='usergroups', to=orm['projects.Project'])),
            ('can_contribute', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('can_moderate', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'users', ['UserGroup'])

        # Adding M2M table for field users on 'UserGroup'
        m2m_table_name = db.shorten_name(u'users_usergroup_users')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('usergroup', models.ForeignKey(orm[u'users.usergroup'], null=False)),
            ('user', models.ForeignKey(orm[u'users.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['usergroup_id', 'user_id'])

        # Adding model 'GroupingUserGroup'
        db.create_table(u'users_groupingusergroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usergroup', self.gf('django.db.models.fields.related.ForeignKey')(related_name='viewgroups', to=orm['users.UserGroup'])),
            ('grouping', self.gf('django.db.models.fields.related.ForeignKey')(related_name='usergroups', to=orm['datagroupings.Grouping'])),
            ('can_read', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('can_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'users', ['GroupingUserGroup'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'users_user')

        # Deleting model 'UserGroup'
        db.delete_table(u'users_usergroup')

        # Removing M2M table for field users on 'UserGroup'
        db.delete_table(db.shorten_name(u'users_usergroup_users'))

        # Deleting model 'GroupingUserGroup'
        db.delete_table(u'users_groupingusergroup')


    models = {
        u'datagroupings.grouping': {
            'Meta': {'object_name': 'Grouping'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isprivate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'groupings'", 'to': u"orm['projects.Project']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
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
        u'users.groupingusergroup': {
            'Meta': {'object_name': 'GroupingUserGroup'},
            'can_read': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'can_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'grouping': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'usergroups'", 'to': u"orm['datagroupings.Grouping']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'usergroup': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'viewgroups'", 'to': u"orm['users.UserGroup']"})
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
        },
        u'users.usergroup': {
            'Meta': {'object_name': 'UserGroup'},
            'can_contribute': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'can_moderate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'usergroups'", 'to': u"orm['projects.Project']"}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['users.User']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['users']