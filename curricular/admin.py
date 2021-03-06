from django.contrib import admin

from curricular.models import *

class CurricularGradeAdmin(admin.ModelAdmin):
    list_display = "title", 'parent'
    list_filter = 'parent', 'user'

class ActivityAdmin(admin.ModelAdmin):
    list_display = 'title', 'subject',
    list_filter = 'subject__subject_class', 'subject',

class ActivityItemAdmin(admin.ModelAdmin):
    list_display = 'order', 'item'

class SubjectAdmin(admin.ModelAdmin):
    list_display = 'title', 'subject_class'
    list_filter = 'subject_class',

class SubjectClassAdmin(admin.ModelAdmin):
    list_display = 'title', 'curricular_grade'
    
admin.site.register(CurricularGrade, CurricularGradeAdmin)
admin.site.register(SubjectClass, SubjectClassAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityItem, ActivityItemAdmin)
admin.site.register(Exercise)
