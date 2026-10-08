from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle

from apps.core.services import ServiceRegistry
from .serializers import HeartAssessmentSerializer


class HeartOptionsView(APIView):
    """Provides metadata, human labels, raw model values, categories, and tooltips for all fields."""

    def get(self, request):
        service = ServiceRegistry.get_heart_service()
        options = service.get_options_schema()
        return Response(options, status=status.HTTP_200_OK)


class HeartAssessView(APIView):
    """Computes risk percentage, SHAP feature importance, and personalized lifestyle recommendations."""
    throttle_scope = 'predict'
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        serializer = HeartAssessmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ServiceRegistry.get_heart_service()
        result = service.assess_risk(serializer.validated_data)

        return Response(result, status=status.HTTP_200_OK)
