import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

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

class Source(models.Model):

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']

    name = models.CharField(blank=True, max_length=500)
    slug = models.CharField(blank=True, max_length=400)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True, verify_exists=True)
    contact_url = models.URLField(blank=True, verify_exists=True)
    contact_email = models.EmailField(blank=True)
    abuse_url = models.URLField(blank=True, verify_exists=True)
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
