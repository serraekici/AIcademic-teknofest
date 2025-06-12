from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    welcome, protected_view, profile_view, schedule_view, upload_exam_file,
    StudentViewSet, CourseViewSet, EventViewSet, ExamScheduleViewSet, LessonScheduleViewSet,
    RegisterView, UserListViewSet, MyTokenObtainPairView,
    ticketmaster_events, local_ticketmaster_events  # Burası önemli
)
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'events', EventViewSet)
router.register(r'exam-schedules', ExamScheduleViewSet)
router.register(r'lesson-schedules', LessonScheduleViewSet)
router.register(r'users', UserListViewSet)

urlpatterns = router.urls + [
    path('', welcome),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', protected_view),
    path('profile/', profile_view),
    path('schedule/', schedule_view),
    path('upload-exam/', upload_exam_file),
    path('register/', RegisterView.as_view()),
    path('ticketmaster-events/', ticketmaster_events),
    path('local-events/', local_ticketmaster_events),  # 🌟 EN ÖNEMLİ SATIR BU 🌟
]
