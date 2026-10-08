from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.renderers import JSONRenderer, BaseRenderer
from django.http import StreamingHttpResponse

from apps.core.services import ServiceRegistry
from .serializers import ChatRequestSerializer


class ServerSentEventRenderer(BaseRenderer):
    media_type = 'text/event-stream'
    format = 'txt'
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class ChatView(APIView):
    """
    Medibot assistant endpoint.
    Accepts {query: string} or {messages: [{role, content}]}
    Supports streaming SSE if stream=True or Accept: text/event-stream.
    """
    throttle_scope = 'chat'
    throttle_classes = [ScopedRateThrottle]
    renderer_classes = [JSONRenderer, ServerSentEventRenderer]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data["query"]
        wants_stream = serializer.validated_data.get("stream", False) or \
            "text/event-stream" in request.headers.get("Accept", "")

        service = ServiceRegistry.get_chatbot_service()

        if wants_stream:
            response = StreamingHttpResponse(
                service.stream_response(query),
                content_type="text/event-stream"
            )
            response["Cache-Control"] = "no-cache"
            response["X-Accel-Buffering"] = "no"
            return response

        try:
            result = service.generate_response(query)
            return Response(
                {
                    "role": "assistant",
                    "content": result["content"],
                    "sources": result["sources"]
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "code": "llm_error",
                    "message": f"Unable to generate response from Medibot: {str(e)}",
                    "fields": {}
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
