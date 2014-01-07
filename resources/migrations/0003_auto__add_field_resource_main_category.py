# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Resource.main_category'
        db.add_column(u'resources_resource', 'main_category',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='main_category_resource_set', to=orm['options.Category']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Resource.main_category'
        db.delete_column(u'resources_resource', 'main_category_id')


    models = {
        u'options.category': {
            'Meta': {'ordering': "['name']", 'object_name': 'Category'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'options.device': {
            'Meta': {'ordering': "['name']", 'object_name': 'Device'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'options.language': {
            'Meta': {'ordering': "['name']", 'object_name': 'Language'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'options.source': {
            'Meta': {'ordering': "['name']", 'object_name': 'Source'},
            'abuse_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'contact_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['options.Language']"}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'tags': ('tagging.fields.TagField', [], {'max_length': '400'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'resources.resource': {
            'Meta': {'ordering': "['-featured', '-pageviews', '-resource_pageviews', '-thumbnails']", 'object_name': 'Resource'},
            'author': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['options.Category']", 'null': 'True', 'blank': 'True'}),
            'content_source': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'custom_resource': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'device': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['options.Device']", 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'globalid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['options.Language']", 'null': 'True', 'blank': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'main_category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'main_category_resource_set'", 'to': u"orm['options.Category']"}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'objective': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pageviews': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 1, 6, 0, 0)'}),
            'resource_download_url': ('django.db.models.fields.URLField', [], {'max_length': '800', 'blank': 'True'}),
            'resource_downloaded_file': ('django.db.models.fields.CharField', [], {'max_length': '800', 'blank': 'True'}),
            'resource_language': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'resource_pageviews': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'resource_reference_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'resource_size': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'resource_url': ('django.db.models.fields.URLField', [], {'max_length': '400', 'blank': 'True'}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['options.Source']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'structure': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {'max_length': '400'}),
            'thumbnails': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '800', 'blank': 'True'}),
            'trigger': ('django.db.models.fields.CharField', [], {'max_length': '400', 'blank': 'True'}),
            'trigger_extension': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'zip_md5': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'})
        }
    }

    complete_apps = ['resources']