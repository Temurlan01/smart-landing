import logging
from datetime import datetime
from django.conf import settings
from api.utils.json_storage import load_json_file, save_json_file

logger = logging.getLogger('api')


class MetricsService:
    """Сервис для сбора метрик"""

    METRICS_FILE = settings.METRICS_FILE

    @classmethod
    def _default_metrics(cls) -> dict:
        return {
            'total_submissions': 0,
            'by_sentiment': {},
            'by_type': {},
            'last_updated': datetime.now().isoformat(),
        }

    @classmethod
    def record_submission(cls, data: dict) -> None:
        """Записывает информацию о контактном обращении"""
        try:
            metrics = cls._load_metrics()

            metrics['total_submissions'] = metrics.get('total_submissions', 0) + 1

            sentiment = data.get('sentiment', 'unknown')
            metrics['by_sentiment'] = metrics.get('by_sentiment', {})
            metrics['by_sentiment'][sentiment] = metrics['by_sentiment'].get(sentiment, 0) + 1

            request_type = data.get('request_type', 'unknown')
            metrics['by_type'] = metrics.get('by_type', {})
            metrics['by_type'][request_type] = metrics['by_type'].get(request_type, 0) + 1

            metrics['last_updated'] = datetime.now().isoformat()

            cls._save_metrics(metrics)
            logger.info("Метрики успешно обновлены")

        except Exception as e:
            logger.error(f"Ошибка при записи метрик: {str(e)}")

    @classmethod
    def get_metrics(cls) -> dict:
        """Возвращает текущие метрики"""
        try:
            metrics = cls._load_metrics()
            if not metrics:
                return cls._default_metrics()
            return metrics
        except Exception as e:
            logger.error(f"Ошибка при получении метрик: {str(e)}")
            return cls._default_metrics()

    @classmethod
    def _load_metrics(cls) -> dict:
        """Загружает метрики из файла"""
        loaded = load_json_file(cls.METRICS_FILE, default=None)
        if not loaded:
            return cls._default_metrics()
        return loaded

    @classmethod
    def _save_metrics(cls, metrics: dict) -> None:
        """Сохраняет метрики в файл"""
        save_json_file(cls.METRICS_FILE, metrics, indent=2)
