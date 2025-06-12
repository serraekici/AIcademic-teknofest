from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from .models import LessonSchedule, ExamSchedule, Course, Student, Event, CustomUser
from .serializers import (
    LessonScheduleSerializer, ExamScheduleSerializer,
    CourseSerializer, StudentSerializer, UserSerializer, RegisterSerializer,
    EventSerializer, MyTokenObtainPairSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
import requests
import os
import json
import pathlib


# JWT Custom View
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# Hoşgeldin endpoint
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
        {"lesson": "Matematik 1", "exam_type": "Vize", "exam_date": "2024-12-05", "exam_time": "10:00"},
        {"lesson": "Fizik 1", "exam_type": "Final", "exam_date": "2024-12-20", "exam_time": "13:30"}
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

# Eski canlı Ticketmaster API sistemin (bunu da koruyorum)
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"

CATEGORIES = {
    "Konser": "music",
    "Festival": "festival",
    "Tiyatro": "theatre",
    "Sergi": "arts & culture",
    "Workshop": "education"
}

def convert_event(e, tag):
    image_url = sorted(e["images"], key=lambda x: x["width"], reverse=True)[0]["url"]
    venue = e.get("_embedded", {}).get("venues", [{}])[0]
    city = venue.get("city", {}).get("name", "Bilinmiyor")
    return {
        "category": tag,
        "title": e["name"],
        "url": e["url"],
        "start": e["dates"]["start"]["localDate"],
        "city": city,
        "image": image_url
    }

@api_view(['GET'])
@permission_classes([AllowAny])
def ticketmaster_events(request):
    results = []
    for tag, classification in CATEGORIES.items():
        params = {
            "countryCode": "TR",
            "classificationName": classification,
            "sort": "date,asc",
            "size": 10,
            "apikey": TICKETMASTER_API_KEY
        }
        response = requests.get(BASE_URL, params=params)
        if not response.ok:
            continue
        events = response.json().get("_embedded", {}).get("events", [])
        if events:
            results.append(convert_event(events[0], tag))
    return Response(results)

# 🌟 BURASI YENİ EKLEDİĞİMİZ LOCAL JSON READER
@api_view(['GET'])
@permission_classes([AllowAny])
def local_ticketmaster_events(request):
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
        etkinlik_path = os.path.join(base_dir, 'etkinlik', 'ticketmaster_data.json')
        with open(etkinlik_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


# ViewSet'ler aynı şekilde kalıyor
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
        user = self.request.query_params.get('user')
        if user:
            return ExamSchedule.objects.filter(user__id=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LessonScheduleViewSet(viewsets.ModelViewSet):
    queryset = LessonSchedule.objects.all()
    serializer_class = LessonScheduleSerializer

    def get_queryset(self):
        user = self.request.query_params.get('user')
        if user:
            return LessonSchedule.objects.filter(user__id=user)
        return super().get_queryset()

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

from django.http import JsonResponse
 
def welcome(request):
    return JsonResponse({"message": "Uygulama Backend Çalışıyor!"})
