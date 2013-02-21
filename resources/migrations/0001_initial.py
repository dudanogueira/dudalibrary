# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Resource'
        db.create_table('resources_resource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('resource_reference_string', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('globalid', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('custom_resource', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=800, blank=True)),
            ('structure', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('objective', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('author', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('content_source', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('license', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('published', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 2, 19, 0, 0))),
            ('size', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('pageviews', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('trigger', self.gf('django.db.models.fields.CharField')(max_length=400, blank=True)),
            ('trigger_extension', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('thumbnails', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('resource_url', self.gf('django.db.models.fields.URLField')(max_length=400, blank=True)),
            ('resource_download_url', self.gf('django.db.models.fields.URLField')(max_length=800, blank=True)),
            ('resource_downloaded_file', self.gf('django.db.models.fields.CharField')(max_length=800, blank=True)),
            ('resource_size', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('resource_pageviews', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('resource_language', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('tags', self.gf('tagging.fields.TagField')(max_length=400)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Source'])),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['options.Language'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
            ('zip_md5', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
        ))
        db.send_create_signal('resources', ['Resource'])

        # Adding M2M table for field category on 'Resource'
        db.create_table('resources_resource_category', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('resource', models.ForeignKey(orm['resources.resource'], null=False)),
            ('category', models.ForeignKey(orm['options.category'], null=False))
        ))
        db.create_unique('resources_resource_category', ['resource_id', 'category_id'])

        # Adding M2M table for field device on 'Resource'
        db.create_table('resources_resource_device', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('resource', models.ForeignKey(orm['resources.resource'], null=False)),
            ('device', models.ForeignKey(orm['options.device'], null=False))
        ))
        db.create_unique('resources_resource_device', ['resource_id', 'device_id'])


    def backwards(self, orm):
        # Deleting model 'Resource'
        db.delete_table('resources_resource')

        # Removing M2M table for field category on 'Resource'
        db.delete_table('resources_resource_category')

        # Removing M2M table for field device on 'Resource'
        db.delete_table('resources_resource_device')


    models = {
        'options.category': {
            'Meta': {'ordering': "['name']", 'object_name': 'Category'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'options.device': {
            'Meta': {'ordering': "['name']", 'object_name': 'Device'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'options.language': {
            'Meta': {'ordering': "['name']", 'object_name': 'Language'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'options.source': {
            'Meta': {'ordering': "['name']", 'object_name': 'Source'},
            'abuse_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'contact_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '400', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'resources.resource': {
            'Meta': {'ordering': "['-featured', '-pageviews', '-resource_pageviews', '-thumbnails']", 'object_name': 'Resource'},
            'author': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['options.Category']", 'null': 'True', 'blank': 'True'}),
            'content_source': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'custom_resource': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'device': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['options.Device']", 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'globalid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['options.Language']", 'null': 'True', 'blank': 'True'}),
            'license': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'objective': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pageviews': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 2, 19, 0, 0)'}),
            'resource_download_url': ('django.db.models.fields.URLField', [], {'max_length': '800', 'blank': 'True'}),
            'resource_downloaded_file': ('django.db.models.fields.CharField', [], {'max_length': '800', 'blank': 'True'}),
            'resource_language': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'resource_pageviews': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'resource_reference_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'resource_size': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'resource_url': ('django.db.models.fields.URLField', [], {'max_length': '400', 'blank': 'True'}),
            'size': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['options.Source']"}),
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