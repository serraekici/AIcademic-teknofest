from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, CourseViewSet  # 👈 burada CourseViewSet var mı?

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'courses', CourseViewSet)  # 👈 bu satır kesinlikle olmalı

urlpatterns = [
    path('', include(router.urls)),
]
