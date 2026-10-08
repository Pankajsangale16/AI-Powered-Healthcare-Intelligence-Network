import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Standardized DRF exception handler returning:
    {
        "code": "error_code",
        "message": "Human readable summary",
        "fields": { ... }
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_code = getattr(exc, 'default_code', 'error')
        message = 'Validation or request error'
        fields = {}

        if isinstance(response.data, dict):
            # If detail is present, use it as main message
            if 'detail' in response.data:
                message = str(response.data['detail'])
                fields = {}
            else:
                fields = response.data
                message = 'One or more fields have validation errors.'
        elif isinstance(response.data, list):
            message = '; '.join(str(item) for item in response.data)
            fields = {'non_field_errors': response.data}
        else:
            message = str(response.data)

        custom_data = {
            'code': str(error_code),
            'message': message,
            'fields': fields
        }
        response.data = custom_data
        return response

    # Unhandled server errors (500)
    logger.exception("Unhandled server exception: %s", exc)
    return Response(
        {
            'code': 'internal_server_error',
            'message': 'An unexpected server error occurred. Please try again later.',
            'fields': {}
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
