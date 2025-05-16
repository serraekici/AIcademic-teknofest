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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": f"Merhaba {request.user.username}, giriş yaptın!"})

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    return Response({
        "username": user.username,
        "email": user.email,
        "date_joined": user.date_joined
    })

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def schedule_view(request):
    # Şimdilik farazi veriler
    data = [
        {
            "lesson": "Matematik 1",
            "exam_type": "Vize",
            "exam_date": "2024-12-05",
            "exam_time": "10:00"
        },
        {
            "lesson": "Fizik 1",
            "exam_type": "Final",
            "exam_date": "2024-12-20",
            "exam_time": "13:30"
        }
    ]
    return Response(data)

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_exam_file(request):
    uploaded_file = request.FILES.get('exam_file')
    
    if uploaded_file:
        # Gelecekte burada yapay zeka işleme yapılacak 🤖
        print(f"Yüklenen dosya: {uploaded_file.name}")
        return Response({"message": "Dosya alındı, işleniyor..."})
    else:
        return Response({"error": "Dosya alınamadı."}, status=400)


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

from rest_framework import viewsets
from .models import Event
from .serializers import EventSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    
from .models import ExamSchedule
from .serializers import ExamScheduleSerializer

class ExamScheduleViewSet(viewsets.ModelViewSet):
    queryset = ExamSchedule.objects.all() 
    serializer_class = ExamScheduleSerializer

    def get_queryset(self):
        return ExamSchedule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

