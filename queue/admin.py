from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

from queue.models import ResourceQueue

class ResourceQueueAdmin(admin.ModelAdmin):
    pass

admin.site.register(ResourceQueue, ResourceQueueAdmin)