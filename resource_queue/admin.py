from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

from models import ResourceQueue

class ResourceQueueAdmin(admin.ModelAdmin):
    list_display = 'identifier_id', 'status', 'priority'
    list_filter = 'status', 'priority'

admin.site.register(ResourceQueue, ResourceQueueAdmin)