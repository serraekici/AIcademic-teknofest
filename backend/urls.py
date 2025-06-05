from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from core.views import welcome    # <-- ekle
 
urlpatterns = [
    path('', welcome),  # <-- Ana sayfa
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
