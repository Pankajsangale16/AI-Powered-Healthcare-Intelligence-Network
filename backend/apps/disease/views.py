from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle

from apps.core.services import ServiceRegistry
from .serializers import DiseasePredictSerializer, DiseaseSearchQuerySerializer


class DiseaseSymptomsListView(APIView):
    """Returns valid symptoms list for search and autocomplete."""

    def get(self, request):
        service = ServiceRegistry.get_disease_service()
        symptoms = service.get_symptoms()
        return Response({"count": len(symptoms), "results": symptoms})


class DiseasePredictView(APIView):
    """Predicts disease based on symptom list, returning precautions, diet, workout, meds."""
    throttle_scope = 'predict'
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        serializer = DiseasePredictSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        symptoms = serializer.validated_data["symptoms"]
        service = ServiceRegistry.get_disease_service()
        result = service.predict(symptoms)

        if not result.get("success"):
            return Response(
                {
                    "code": "invalid_symptoms",
                    "message": result.get("error", "Unable to match symptoms."),
                    "fields": {"symptoms": [result.get("error")]}
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(result, status=status.HTTP_200_OK)


class DiseaseSearchView(APIView):
    """Searches disease names and returns descriptions and recommendations."""

    def get(self, request):
        serializer = DiseaseSearchQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data["q"]
        service = ServiceRegistry.get_disease_service()
        matches = service.search(query)

        return Response({
            "query": query,
            "count": len(matches),
            "results": matches
        })
