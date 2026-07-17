import logging
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('api')


def custom_exception_handler(exc, context):
    """
    Глобальный handler для всех ошибок API
    """
    response = exception_handler(exc, context)

    if response is None:
        logger.error(f"Непредвиденная ошибка: {str(exc)}", exc_info=True)
        detail = str(exc) if settings.DEBUG else 'Произошла неожиданная ошибка'
        return Response(
            {
                'error': 'Внутренняя ошибка сервера',
                'detail': detail,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    if response.status_code >= 400:
        logger.warning(f"API Error {response.status_code}: {response.data}")

    return response
