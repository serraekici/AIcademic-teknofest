from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings



class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    university = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    credits = models.IntegerField()

    def __str__(self):
        return f'{self.code} - {self.name}'

class Event(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    location = models.CharField(max_length=200)
    is_online = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class ExamSchedule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    course_name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=50)
    exam_date = models.DateField()
    exam_time = models.TimeField()
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.course_name} ({self.exam_date})"

class LessonSchedule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=100)
    day_of_week = models.CharField(max_length=10)  # Pazartesi, Salı vb.
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.course_name} ({self.day_of_week})"
    
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    student_id = models.CharField(max_length=20, blank=True)
    university = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.username
