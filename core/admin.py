from django.contrib import admin

from .models import ExamSchedule, LessonSchedule

admin.site.register(ExamSchedule)
admin.site.register(LessonSchedule)

