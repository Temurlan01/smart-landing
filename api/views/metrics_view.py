import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from api.services import MetricsService

logger = logging.getLogger('api')

@api_view(['GET'])
def metrics_view(request):
    """
    Получить статистику обращений
    GET /api/metrics
    """
    try:
        metrics = MetricsService.get_metrics()
        return Response(metrics, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Ошибка при получении метрик: {str(e)}")
        return Response(
            {'error': 'Не удалось получить метрики'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )