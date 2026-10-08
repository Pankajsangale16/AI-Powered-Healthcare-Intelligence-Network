from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.core.services import ServiceRegistry
from .serializers import DrugSearchSerializer, DrugRecommendSerializer


class DrugListView(APIView):
    """Paginated search for medicines across the 9,720 drug dataset."""

    def get(self, request):
        serializer = DrugSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        params = serializer.validated_data
        service = ServiceRegistry.get_drug_service()
        results = service.search_drugs(
            query=params["q"],
            page=params["page"],
            page_size=params["page_size"]
        )
        return Response(results, status=status.HTTP_200_OK)


class DrugRecommendView(APIView):
    """Finds top 5 similar medicines using NLP and cosine similarity."""

    def post(self, request):
        serializer = DrugRecommendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        medicine = serializer.validated_data["medicine"]
        service = ServiceRegistry.get_drug_service()
        result = service.recommend(medicine)

        if not result.get("success"):
            return Response(
                {
                    "code": "medicine_not_found",
                    "message": result.get("error", "Medicine not found."),
                    "fields": {"medicine": [result.get("error")]}
                },
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(result, status=status.HTTP_200_OK)
