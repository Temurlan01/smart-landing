import logging
from datetime import datetime, timedelta
from django.conf import settings
from api.utils.json_storage import load_json_file, save_json_file

logger = logging.getLogger('api')


class RateLimitService:
    """Сервис для защиты от спама"""

    RATE_LIMIT_FILE = settings.RATE_LIMIT_FILE

    @classmethod
    def is_allowed(cls, identifier: str) -> bool:
        """
        Проверяет, разрешен ли запрос для данного идентификатора (IP или email)
        """
        try:
            current_time = datetime.now()
            limit_time_window = current_time - timedelta(minutes=settings.RATE_LIMIT_MINUTES)

            data = cls._load_data()

            if identifier not in data:
                data[identifier] = []

            data[identifier] = [
                timestamp for timestamp in data[identifier]
                if datetime.fromisoformat(timestamp) > limit_time_window
            ]

            if len(data[identifier]) >= settings.RATE_LIMIT_REQUESTS:
                logger.warning(f"Превышен лимит запросов для {identifier}")
                cls._save_data(data)
                return False

            data[identifier].append(current_time.isoformat())
            cls._save_data(data)

            return True

        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            return True

    @classmethod
    def _load_data(cls) -> dict:
        """Загружает данные rate limiting из файла"""
        return load_json_file(cls.RATE_LIMIT_FILE, default={})

    @classmethod
    def _save_data(cls, data: dict) -> None:
        """Сохраняет данные rate limiting в файл"""
        save_json_file(cls.RATE_LIMIT_FILE, data)
