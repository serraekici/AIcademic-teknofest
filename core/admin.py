from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import ExamSchedule, LessonSchedule

admin.site.register(ExamSchedule)
admin.site.register(LessonSchedule)
admin.site.register(CustomUser, UserAdmin)
