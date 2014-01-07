from django.contrib.gis import admin

from options.models import Category, Language, Source, Device

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name',)

class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'code',)
    
class SourceAdmin(admin.GeoModelAdmin):
    pass

class DeviceAdmin(admin.ModelAdmin):
    pass

admin.site.register(Category, CategoryAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Device, DeviceAdmin)