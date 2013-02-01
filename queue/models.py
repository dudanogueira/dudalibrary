# -*- coding: utf-8 -*-
from django.db import models
from dudalibrary.utils import resource_identifier, activity_queued_item_delivery
import datetime

from django.contrib.auth.models import User

RESOURCE_QUEUE_STATUS_CHOICES = (
    ('queued', 'Queued'),
    ('done', 'Done'),
    ('error', 'Error'),
)

class ResourceQueue(models.Model):
    
    def __unicode__(self):
        return "Queue for %s" % self.identifier_id
    
    def run(self):
        '''
        run the queued resource according to the plugin_name
        '''
        # load parser
        if self.identifier_id and self.plugin_name:
            parsed = resource_identifier(
                url=self.identifier_id,
                plugin_slug=self.plugin_slug
            )
            if parsed and parsed.identified:
                try:
                    parsed.parse(self.identifier_id)
                    parsed.index()
                    parsed.download()
                    activity_queued_item_delivery(self, parsed.resource)
                    self.status = "done"
                    self.save()
                    return parsed
                except:
                    raise
                    self.status = 'error'
                    # increase tries TODO
                    # self.tries += 1
                    self.save()
                    return False
        
    
    status = models.CharField(blank=False, default="queued", max_length=100, choices=RESOURCE_QUEUE_STATUS_CHOICES)
    full_url = models.URLField(blank=True, verify_exists=False)
    identifier_id = models.CharField(blank=False, null=False, max_length=500)
    plugin_name = models.CharField(blank=False, null=False, max_length=300)
    plugin_slug = models.CharField(blank=False, null=False, max_length=100)
    log = models.TextField(blank=True, null=True)
    runned = models.DateTimeField(blank=True, null=True)
    request_user = models.ForeignKey(User)
    # metadata information
    created = models.DateTimeField(blank=True, auto_now_add=True)
    updated = models.DateTimeField(blank=True, auto_now=True)
