# -*- coding: utf-8 -*-
import json

from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from observationtypes.models import Field, LookupValue, MultipleLookupValue


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        for observation in orm.Observation.objects.all():
            search_matches = []

            for field in Field.objects.filter(
                    observationtype_id=observation.observationtype_id):

            # for field in observation.observationtype.fields.all():
                if field.key in observation.attributes.keys():

                    if field.fieldtype == 'TextField':
                        term = observation.attributes.get(field.key)
                        if term is not None:
                            search_matches.append('%s:%s' % (field.key, term))

                    elif field.fieldtype == 'LookupField':
                        l_id = observation.attributes.get(field.key)
                        try:
                            lookup = field.lookupvalues.get(pk=l_id)
                            search_matches.append('%s:%s' % (field.key, lookup.name))
                        except LookupValue.DoesNotExist:
                            pass

                    elif field.fieldtype == 'MultipleLookupField':
                        terms = observation.attributes.get(field.key)
                        if terms is not None:
                            l_ids = json.loads(terms)

                            for l_id in l_ids:
                                try:
                                    lookup = field.lookupvalues.get(pk=l_id)
                                    search_matches.append('%s:%s' % (field.key, lookup.name))
                                except MultipleLookupValue.DoesNotExist:
                                    pass

            observation.search_matches = '#####'.join(search_matches)
            observation.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        'contributions.comment': {
            'Meta': {'object_name': 'Comment'},
            'commentto': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['contributions.Observation']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'respondsto': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'responses'", 'null': 'True', 'to': "orm['contributions.Comment']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'contributions.historicalobservation': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalObservation'},
            'attributes': (u'django_hstore.fields.DictionaryField', [], {'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'creator_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']", 'null': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'location_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'observationtype_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'project_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'review_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'search_matches': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'updator_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'contributions.imagefile': {
            'Meta': {'object_name': 'ImageFile', '_ormbases': ['contributions.MediaFile']},
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'mediafile_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['contributions.MediaFile']", 'unique': 'True', 'primary_key': 'True'})
        },
        'contributions.location': {
            'Meta': {'object_name': 'Location'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.GeometryField', [], {'geography': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'private_for_project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']", 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'contributions.mediafile': {
            'Meta': {'object_name': 'MediaFile'},
            'contribution': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files_attached'", 'to': "orm['contributions.Observation']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'contributions.observation': {
            'Meta': {'object_name': 'Observation'},
            'attributes': (u'django_hstore.fields.DictionaryField', [], {'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'creator'", 'to': u"orm['users.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'locations'", 'to': "orm['contributions.Location']"}),
            'observationtype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['observationtypes.ObservationType']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'observations'", 'to': u"orm['projects.Project']"}),
            'review_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'search_matches': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'updator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'updator'", 'null': 'True', 'to': u"orm['users.User']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'observationtypes.observationtype': {
            'Meta': {'object_name': 'ObservationType'},
            'colour': ('django.db.models.fields.TextField', [], {'default': "'#0033ff'"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'default_status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '20'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'observationtypes'", 'to': u"orm['projects.Project']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'symbol': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'})
        },
        u'projects.project': {
            'Meta': {'object_name': 'Project'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'admins'", 'symmetrical': 'False', 'to': u"orm['users.User']"}),
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

    complete_apps = ['contributions']
    symmetrical = True
