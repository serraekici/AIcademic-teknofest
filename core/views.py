from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Course
from .models import Student
from .serializers import CourseSerializer
from rest_framework import viewsets
from .serializers import StudentSerializer
from .serializers import UserSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


def welcome(request):
    return JsonResponse({"message": "Uygulama Backend Calisiyor!"})


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class UserListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


