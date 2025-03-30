from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
from rest_framework import viewsets
from .models import Student
from .serializers import StudentSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


def welcome(request):
    return JsonResponse({"message": "Uygulama Backend Calisiyor!"})
