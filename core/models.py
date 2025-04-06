from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    university = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


from django.db import models

class Course(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    credits = models.IntegerField()

    def __str__(self):
        return f'{self.code} - {self.name}'
    
from django.contrib.auth.models import User

class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='schedules')
    title = models.CharField(max_length=100)  # örn: "Vize Sınavı", "Ders Saati"
    date = models.DateField()                # sadece tarih
    time = models.TimeField(null=True, blank=True)  # saat opsiyonel
    description = models.TextField(blank=True)      # açıklama

    def __str__(self):
        return f"{self.course.name} - {self.title} ({self.date})"
