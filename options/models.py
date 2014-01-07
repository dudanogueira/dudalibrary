import datetime, os
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from django.contrib.sites.models import Site

import tagging
from tagging.fields import TagField

# Create your models here.
class Category(models.Model):

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

    name = models.CharField(blank=True, max_length=300, verbose_name=_("Category Name"))
    code = models.CharField(blank=True, max_length=100)
    summary = models.TextField(blank=True)

class Language(models.Model):

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']        

    def translanted_name(self):
        try:
            string = settings.CONTENT_LANGUAGES[self.code]
        except:
            string = self.name
        return string

    name = models.CharField(blank=True, max_length=100, verbose_name=_("Language Name"))
    code = models.CharField(blank=True, max_length=100, verbose_name=_("Language ISO Code"))


def get_upload_path_logo(instance, filename):
    return os.path.join("source_%s/logo/" % instance.slug, filename)

class Source(models.Model):

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse("source_details", args=[str(self.id)])

    absolute_url = property(get_absolute_url)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
    
    def domain(self):
        if not self.url:
            current_site = Site.objects.get_current()
            return current_site.domain
        else:
            return self.url
    
    objects = models.GeoManager()

    logo = models.ImageField(upload_to=get_upload_path_logo, blank=True, null=True)
    point = models.PointField(blank=True, null=True)
    name = models.CharField(blank=True, max_length=500)
    slug = models.CharField(blank=False, null=False, max_length=400)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    contact_url = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    abuse_url = models.URLField(blank=True)
    language = models.ForeignKey('Language')
    # tags
    tags = TagField(max_length=400)
    # metadata information
    created = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True)
    updated = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True)
    enabled = models.BooleanField(default=False)

class Device(models.Model):

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

    name = models.CharField(blank=True, null=True, max_length=300, verbose_name=_("Device Display Name"))
    summary = models.TextField(blank=True, null=True)

# tagging conf
tagging.register(Source, tag_descriptor_attr="tag_handler")