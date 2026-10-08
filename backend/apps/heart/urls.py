from django.urls import path
from .views import HeartOptionsView, HeartAssessView

urlpatterns = [
    path('options/', HeartOptionsView.as_view(), name='heart-options'),
    path('assess/', HeartAssessView.as_view(), name='heart-assess'),
]
