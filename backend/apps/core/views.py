from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
import os


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "status": "healthy",
                "service": "AI-Powered Healthcare Intelligence Network API",
                "version": "1.0.0",
                "groq_configured": bool(os.environ.get("GROQ_API_KEY")),
            },
            status=status.HTTP_200_OK
        )
