from django.contrib import admin

from curricular.models import *

class CurricularGradeAdmin(admin.ModelAdmin):
    pass

class ActivityAdmin(admin.ModelAdmin):
    list_display = 'title', 'subject',
    list_filter = 'subject__subject_class', 'subject',

class ActivityItemAdmin(admin.ModelAdmin):
    list_display = 'order', 'item'

class SubjectAdmin(admin.ModelAdmin):
    list_display = 'title',
    list_filter = 'subject_class',
    
admin.site.register(CurricularGrade, CurricularGradeAdmin)
admin.site.register(SubjectClass)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityItem, ActivityItemAdmin)
admin.site.register(Exercise)
