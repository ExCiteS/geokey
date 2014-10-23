# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from projects.models import Project, Admins
from users.models import User


class ProjectAdminsMock(models.Model):
    class Meta:
        db_table = u'projects_project_admins'

    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Admins'
        db.create_table(u'projects_admins', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='admin_of', to=orm['projects.Project'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='has_admins', to=orm['users.User'])),
            ('contact', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'projects', ['Admins'])

        # Adding unique constraint on 'Admins', fields ['project', 'user']
        db.create_unique(u'projects_admins', ['project_id', 'user_id'])

        # Mirgrate M2M Project-admins relation
        admins = []
        for data in ProjectAdminsMock.objects.all():
            try:
                admins.append(Admins(
                    project=data.project,
                    user=data.user
                ))
            except Project.DoesNotExist:
                pass

        Admins.objects.bulk_create(admins)

        # Removing M2M table for field admins on 'Project'
        db.delete_table(db.shorten_name(u'projects_project_admins'))


    def backwards(self, orm):
        # Removing unique constraint on 'Admins', fields ['project', 'user']
        db.delete_unique(u'projects_admins', ['project_id', 'user_id'])

        # Deleting model 'Admins'
        db.delete_table(u'projects_admins')

        # Adding M2M table for field admins on 'Project'
        m2m_table_name = db.shorten_name(u'projects_project_admins')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm[u'projects.project'], null=False)),
            ('user', models.ForeignKey(orm[u'users.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['project_id', 'user_id'])


    models = {
        u'projects.admins': {
            'Meta': {'unique_together': "(('project', 'user'),)", 'object_name': 'Admins'},
            'contact': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admin_of'", 'to': u"orm['projects.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'has_admins'", 'to': u"orm['users.User']"})
        },
        u'projects.project': {
            'Meta': {'object_name': 'Project'},
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

    complete_apps = ['projects']
