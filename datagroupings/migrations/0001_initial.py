# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Grouping'
        db.create_table(u'datagroupings_grouping', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('isprivate', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=20)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='groupings', to=orm['projects.Project'])),
        ))
        db.send_create_signal(u'datagroupings', ['Grouping'])

        # Adding model 'Rule'
        db.create_table(u'datagroupings_rule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('grouping', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rules', to=orm['datagroupings.Grouping'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['categories.Category'])),
            ('min_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('max_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('filters', self.gf(u'django_hstore.fields.DictionaryField')(default=None, null=True, db_index=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=20)),
        ))
        db.send_create_signal(u'datagroupings', ['Rule'])


    def backwards(self, orm):
        # Deleting model 'Grouping'
        db.delete_table(u'datagroupings_grouping')

        # Deleting model 'Rule'
        db.delete_table(u'datagroupings_rule')


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
        u'datagroupings.rule': {
            'Meta': {'object_name': 'Rule'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['categories.Category']"}),
            'filters': (u'django_hstore.fields.DictionaryField', [], {'default': 'None', 'null': 'True', 'db_index': 'True'}),
            'grouping': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rules'", 'to': u"orm['datagroupings.Grouping']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'min_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
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

    complete_apps = ['datagroupings']