from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser

from .models import (
    Course, Student, Event, ExamSchedule, LessonSchedule, CustomUser
)
from .serializers import (
    CourseSerializer, StudentSerializer, UserSerializer, RegisterSerializer,
    EventSerializer, ExamScheduleSerializer, LessonScheduleSerializer,
    MyTokenObtainPairSerializer
)

# JWT Custom View
from rest_framework_simplejwt.views import TokenObtainPairView
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

def welcome(request):
    return JsonResponse({"message": "Uygulama Backend Calisiyor!"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": f"Merhaba {request.user.username}, giriş yaptın!"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    return Response({
        "username": user.username,
        "email": user.email,
        "date_joined": user.date_joined
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def schedule_view(request):
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

@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_exam_file(request):
    uploaded_file = request.FILES.get('exam_file')
    if uploaded_file:
        print(f"Yüklenen dosya: {uploaded_file.name}")
        return Response({"message": "Dosya alındı, işleniyor..."})
    else:
        return Response({"error": "Dosya alınamadı."}, status=400)
from django.http import JsonResponse

def welcome(request):
    return JsonResponse({"message": "Uygulama Backend Çalışıyor!"})
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class ExamScheduleViewSet(viewsets.ModelViewSet):
    queryset = ExamSchedule.objects.all()
    serializer_class = ExamScheduleSerializer

    def get_queryset(self):
        return ExamSchedule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LessonScheduleViewSet(viewsets.ModelViewSet):
    queryset = LessonSchedule.objects.all()
    serializer_class = LessonScheduleSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
