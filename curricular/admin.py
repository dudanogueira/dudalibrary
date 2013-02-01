from django.contrib import admin

from curricular.models import *

class CurricularGradeAdmin(admin.ModelAdmin):
    pass

class ActivityItemAdmin(admin.ModelAdmin):
    list_display = 'order', 'item'
    
admin.site.register(CurricularGrade, CurricularGradeAdmin)
admin.site.register(SubjectClass)
admin.site.register(Subject)
admin.site.register(Activity)
admin.site.register(ActivityItem, ActivityItemAdmin)
admin.site.register(Exercise)
