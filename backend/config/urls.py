from django.contrib import admin
from django.urls import path, include
from apps.core.views import HealthCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', HealthCheckView.as_view(), name='api-health'),
    path('api/v1/disease/', include('apps.disease.urls')),
    path('api/v1/drugs/', include('apps.drugs.urls')),
    path('api/v1/heart/', include('apps.heart.urls')),
    path('api/v1/chat/', include('apps.chatbot.urls')),
]
