from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    welcome, protected_view, profile_view, schedule_view, upload_exam_file,
    StudentViewSet, CourseViewSet, EventViewSet, ExamScheduleViewSet, LessonScheduleViewSet,
    RegisterView, UserListViewSet, MyTokenObtainPairView
)

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'events', EventViewSet)
router.register(r'exam-schedules', ExamScheduleViewSet)
router.register(r'lesson-schedules', LessonScheduleViewSet)
router.register(r'users', UserListViewSet)

urlpatterns = [
    path('', welcome, name='welcome'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),   # 👈 kendi JWT login endpointin
    path('protected/', protected_view, name='protected'),
    path('profile/', profile_view, name='profile'),
    path('schedule/', schedule_view, name='schedule'),
    path('upload-exam/', upload_exam_file, name='upload_exam_file'),
    path('register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
]
