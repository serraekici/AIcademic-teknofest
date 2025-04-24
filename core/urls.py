from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, CourseViewSet  # 👈 burada CourseViewSet var mı?
from .views_auth import RegisterView, LoginView
from django.urls import path
from .views import RegisterView
from .views import UserListViewSet
from .views import protected_view

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'courses', CourseViewSet)  # 👈 bu satır kesinlikle olmalı
router.register(r'users', UserListViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('protected/', protected_view, name='protected'),
]



