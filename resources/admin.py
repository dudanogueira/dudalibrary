from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

from resources.models import *

def generate_descriptor(modeladmin, request, queryset):
    for obj in queryset:
        obj.generate_descriptor()
generate_descriptor.short_description = "Generate Content JSON Descriptor"

def generate_pack(modeladmin, request, queryset):
    for obj in queryset:
        obj.generate_pack()
generate_pack.short_description = "Build Content Pack at the repository"

class ResourceAdmin(admin.ModelAdmin):
    actions = [generate_descriptor, generate_pack]
    list_display = ('id', 'enabled','title','status','resource_downloaded_file')
    list_display_links = list_display
    list_filter = ('enabled', 'status', 'source', 'category', 'language', 'device',)
    search_fields = ['title', 'objective', 'structure']
    
admin.site.register(Resource, ResourceAdmin)