from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, CourseViewSet  # 👈 burada CourseViewSet var mı?
from .views_auth import RegisterView, LoginView
from django.urls import path
from .views import RegisterView
from .views import UserListViewSet
from .views import protected_view
from .views import profile_view
from .views import schedule_view
from .views import upload_exam_file
from .views import EventViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'courses', CourseViewSet)  # 👈 bu satır kesinlikle olmalı
router.register(r'users', UserListViewSet)
router.register(r'events', EventViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('protected/', protected_view, name='protected'),
    path('profile/', profile_view, name='profile'),
    path('schedule/', schedule_view, name='schedule'),
    path('upload-exam/', upload_exam_file, name='upload_exam'),
    path('', include(router.urls)),
]



