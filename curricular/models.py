import datetime

from options.models import Language
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import tagging
from tagging.fields import TagField
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class CurricularGrade(models.Model):

    def __unicode__(self):
        if not self.parent:
            return u'%s' % self.title
        else:
            return u'%s - %s' % (self.parent, self.title)

    parent = models.ForeignKey('self', blank=True, null=True, limit_choices_to = {'parent': None})
    title = models.CharField(blank=False, null=False, max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    # metadata information
    created = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True)
    updated = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True)

class SubjectClass(models.Model):
    '''1 Serie, 2 Serie, etc'''

    def __unicode__(self):
        return u'%s' % self.title
    
    curricular_grade = models.ForeignKey(CurricularGrade)
    title = models.CharField(_("Title"), blank=False, null=False, max_length=100)
    description = models.TextField(_("Description"), blank=True)
    # metadata information
    created = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True)
    updated = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True)

class Subject(models.Model):
    
    def __unicode__(self):
        #return u'%s (%s)' % (self.title, self.subject_class.title)
        return u'%s' % self.title
    
    class Meta:
        ordering = ['title']

    title = models.CharField(blank=False, null=False, max_length=100)
    subject_class = models.ForeignKey(SubjectClass)
    description = models.TextField(blank=True)
    # metadata information
    created = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True)
    updated = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True)

class ActivityItem(models.Model):

    def __unicode__(self):
        try:
            output = u'%s (%s)' % (self.item.title, self.content_type)
        except:
            output = u'%s' % self.item
        return output

    class Meta:
        unique_together = (('activity', 'order'),)

    '''Relative to an Exercise or Resource'''
    order = models.IntegerField(blank=False, null=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    item = generic.GenericForeignKey('content_type', 'object_id')
    activity = models.ForeignKey('Activity')
    # metadata information
    created = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True)
    updated = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True)

class Activity(models.Model):
    
    @models.permalink
    def get_absolute_url(self):
        return ('activity_details', (), 
            {
            'object_id': str(self.id),
            }
        )
    
    
    def __unicode__(self):
        return u'%s' % self.title
    
    subject = models.ForeignKey(Subject)
    title = models.CharField(blank=False, max_length=100)
    description = models.TextField(blank=True)
    tags = TagField(max_length=400)
    # metadata information
    created = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True)
    updated = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True)

class Exercise(models.Model):
    
    def __unicode__(self):
        return u'%s' % self.title
    
    title = models.CharField(blank=True, max_length=100)
    description = models.TextField(blank=True)
    tags = TagField(max_length=400)
    # metadata information
    created = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now_add=True)
    updated = models.DateTimeField(blank=True, default=datetime.datetime.now, auto_now=True)    

# tagging conf
tagging.register(Activity, tag_descriptor_attr="tag_handler")
tagging.register(Exercise, tag_descriptor_attr="tag_handler")