import logging
from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger('api')


class ErrorHandlerMiddleware:
    """Middleware для глобальной обработки ошибок"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.error(f"Непредвиденная ошибка: {str(e)}", exc_info=True)
            detail = str(e) if settings.DEBUG else 'Произошла неожиданная ошибка'
            return JsonResponse(
                {
                    'error': 'Внутренняя ошибка сервера',
                    'detail': detail,
                },
                status=500
            )
