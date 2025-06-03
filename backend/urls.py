from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),  # Tüm core app endpointleri buradan gelir
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # İstersen ana sayfa için küçük bir karşılama mesajı:
    # path('', lambda r: JsonResponse({'message': 'API Running!'})),
]
