from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from api.services import AIService, EmailService, RateLimitService, MetricsService
from django.conf import settings
from pathlib import Path
import json
import tempfile


class AIServiceTest(TestCase):
    """Тесты для AIService"""

    def setUp(self):
        """Создаем экземпляр сервиса перед каждым тестом"""
        AIService._api_disabled = False
        self.ai_service = AIService()

    def test_fallback_sentiment_analysis_positive(self):
        """Тест fallback анализа тональности - позитивный"""
        text = "Отлично, просто превосходно! Все очень хорошо"
        result = self.ai_service._fallback_sentiment_analysis(text)
        self.assertEqual(result['sentiment'], 'positive')
        self.assertGreater(result['score'], 0.5)

    def test_fallback_sentiment_analysis_negative(self):
        """Тест fallback анализа тональности - негативный"""
        text = "Плохо, ужасно, кошмар! Очень недоволен"
        result = self.ai_service._fallback_sentiment_analysis(text)
        self.assertEqual(result['sentiment'], 'negative')
        self.assertLess(result['score'], 0.5)

    def test_fallback_sentiment_analysis_neutral(self):
        """Тест fallback анализа тональности - нейтральный"""
        text = "Обычный текст без эмоций"
        result = self.ai_service._fallback_sentiment_analysis(text)
        self.assertEqual(result['sentiment'], 'neutral')
        self.assertEqual(result['score'], 0.5)

    def test_fallback_classification_inquiry(self):
        """Тест fallback классификации - запрос"""
        text = "У меня есть вопрос о вашем проекте"
        result = self.ai_service._fallback_classification(text)
        self.assertEqual(result['type'], 'inquiry')

    def test_fallback_classification_feedback(self):
        """Тест fallback классификации - отзыв"""
        text = "Хочу оставить отзыв о вашей работе"
        result = self.ai_service._fallback_classification(text)
        self.assertEqual(result['type'], 'feedback')

    def test_fallback_classification_collaboration(self):
        """Тест fallback классификации - сотрудничество"""
        text = "Предлагаю сотрудничество над проектом"
        result = self.ai_service._fallback_classification(text)
        self.assertEqual(result['type'], 'collaboration')

    def test_fallback_classification_support(self):
        """Тест fallback классификации - поддержка"""
        text = "У меня проблема, помогите пожалуйста"
        result = self.ai_service._fallback_classification(text)
        self.assertEqual(result['type'], 'support')

    def test_fallback_classification_other(self):
        """Тест fallback классификации - другое"""
        text = "xyz abc def"  # Текст без ключевых слов
        result = self.ai_service._fallback_classification(text)
        self.assertEqual(result['type'], 'other')

    def test_fallback_response(self):
        """Тест fallback генерации ответа"""
        name = "Ivan"
        response = self.ai_service._fallback_response(name)
        self.assertIn(name, response)
        self.assertIn("спасибо", response.lower())

    @override_settings(OPENAI_API_KEY='')
    def test_analyze_sentiment_without_api_key(self):
        """Тест анализа тональности без API ключа"""
        result = self.ai_service.analyze_sentiment("Test comment")
        self.assertIn('sentiment', result)
        self.assertIn('score', result)
        self.assertIn('reasoning', result)

    @patch('api.services.ai_service.OpenAI')
    @override_settings(OPENAI_API_KEY='test-key')
    def test_analyze_sentiment_with_api_key(self, mock_openai_cls):
        """Тест анализа тональности с API ключом"""
        AIService._api_disabled = False
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = (
            '{"sentiment": "positive", "score": 0.9, "reasoning": "Test"}'
        )
        mock_client.chat.completions.create.return_value = mock_response

        ai_service = AIService()
        result = ai_service.analyze_sentiment("Test comment")
        self.assertEqual(result['sentiment'], 'positive')
        self.assertEqual(result['score'], 0.9)

    @patch('api.services.ai_service.OpenAI')
    @override_settings(OPENAI_API_KEY='test-key')
    def test_analyze_sentiment_with_api_error(self, mock_openai_cls):
        """Тест анализа тональности с ошибкой API"""
        AIService._api_disabled = False
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        ai_service = AIService()
        result = ai_service.analyze_sentiment("Test comment")
        self.assertIn('sentiment', result)  # Fallback should work


class EmailServiceTest(TestCase):
    """Тесты для EmailService"""

    @patch('api.services.email_service.send_mail')
    def test_send_contact_confirmation_success(self, mock_send_mail):
        """Тест успешной отправки подтверждения"""
        contact_data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'Test comment'
        }
        mock_send_mail.return_value = True
        
        result = EmailService.send_contact_confirmation(contact_data)
        self.assertTrue(result)
        mock_send_mail.assert_called_once()

    @patch('api.services.email_service.send_mail')
    def test_send_contact_confirmation_failure(self, mock_send_mail):
        """Тест неудачной отправки подтверждения"""
        contact_data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'Test comment'
        }
        mock_send_mail.side_effect = Exception("SMTP Error")
        
        result = EmailService.send_contact_confirmation(contact_data)
        self.assertFalse(result)

    @patch('api.services.email_service.send_mail')
    def test_send_admin_notification_success(self, mock_send_mail):
        """Тест успешной отправки уведомления админу"""
        contact_data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'Test comment',
            'sentiment': 'positive',
            'request_type': 'inquiry'
        }
        mock_send_mail.return_value = True
        
        result = EmailService.send_admin_notification(contact_data)
        self.assertTrue(result)
        mock_send_mail.assert_called_once()

    @patch('api.services.email_service.send_mail')
    def test_send_admin_notification_failure(self, mock_send_mail):
        """Тест неудачной отправки уведомления админу"""
        contact_data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'Test comment'
        }
        mock_send_mail.side_effect = Exception("SMTP Error")
        
        result = EmailService.send_admin_notification(contact_data)
        self.assertFalse(result)


class RateLimitServiceTest(TestCase):
    """Тесты для RateLimitService"""

    def setUp(self):
        """Создаем временный файл для rate limit данных"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        # Патчим путь к файлу
        self.original_file = settings.RATE_LIMIT_FILE
        settings.RATE_LIMIT_FILE = Path(self.temp_file.name)
        RateLimitService.RATE_LIMIT_FILE = settings.RATE_LIMIT_FILE

    def tearDown(self):
        """Удаляем временный файл после тестов"""
        import os
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        settings.RATE_LIMIT_FILE = self.original_file
        RateLimitService.RATE_LIMIT_FILE = self.original_file

    @override_settings(RATE_LIMIT_REQUESTS=5, RATE_LIMIT_MINUTES=10)
    def test_is_allowed_first_request(self):
        """Тест первого запроса - должен быть разрешен"""
        result = RateLimitService.is_allowed('127.0.0.1')
        self.assertTrue(result)

    @override_settings(RATE_LIMIT_REQUESTS=5, RATE_LIMIT_MINUTES=10)
    def test_is_allowed_within_limit(self):
        """Тест запросов в пределах лимита"""
        for i in range(5):
            result = RateLimitService.is_allowed('127.0.0.1')
            self.assertTrue(result, f"Request {i+1} should be allowed")

    @override_settings(RATE_LIMIT_REQUESTS=3, RATE_LIMIT_MINUTES=10)
    def test_is_allowed_exceeds_limit(self):
        """Тест превышения лимита"""
        for i in range(3):
            RateLimitService.is_allowed('127.0.0.1')
        
        result = RateLimitService.is_allowed('127.0.0.1')
        self.assertFalse(result)

    @override_settings(RATE_LIMIT_REQUESTS=5, RATE_LIMIT_MINUTES=10)
    def test_is_allowed_different_ips(self):
        """Тест разных IP адресов"""
        for i in range(5):
            result = RateLimitService.is_allowed(f'192.168.1.{i}')
            self.assertTrue(result)

    @override_settings(RATE_LIMIT_REQUESTS=2, RATE_LIMIT_MINUTES=10)
    def test_is_allowed_after_time_window(self):
        """Тест сброса лимита после временного окна"""
        # Создаем старые записи
        data = {
            '127.0.0.1': ['2024-01-01T00:00:00', '2024-01-01T00:00:01']
        }
        with open(settings.RATE_LIMIT_FILE, 'w') as f:
            json.dump(data, f)
        
        # Новый запрос должен быть разрешен (старые записи удалены)
        result = RateLimitService.is_allowed('127.0.0.1')
        self.assertTrue(result)


class MetricsServiceTest(TestCase):
    """Тесты для MetricsService"""

    def setUp(self):
        """Создаем временный файл для метрик"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        # Патчим путь к файлу
        self.original_file = settings.METRICS_FILE
        settings.METRICS_FILE = Path(self.temp_file.name)
        MetricsService.METRICS_FILE = settings.METRICS_FILE

    def tearDown(self):
        """Удаляем временный файл после тестов"""
        import os
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        settings.METRICS_FILE = self.original_file
        MetricsService.METRICS_FILE = self.original_file

    def test_record_submission(self):
        """Тест записи новой метрики"""
        submission_data = {
            'sentiment': 'positive',
            'request_type': 'inquiry'
        }
        MetricsService.record_submission(submission_data)
        
        metrics = MetricsService.get_metrics()
        self.assertEqual(metrics['total_submissions'], 1)
        self.assertEqual(metrics['by_sentiment']['positive'], 1)
        self.assertEqual(metrics['by_type']['inquiry'], 1)

    def test_record_multiple_submissions(self):
        """Тест записи нескольких метрик"""
        submissions = [
            {'sentiment': 'positive', 'request_type': 'inquiry'},
            {'sentiment': 'neutral', 'request_type': 'feedback'},
            {'sentiment': 'negative', 'request_type': 'support'}
        ]
        
        for submission in submissions:
            MetricsService.record_submission(submission)
        
        metrics = MetricsService.get_metrics()
        self.assertEqual(metrics['total_submissions'], 3)
        self.assertEqual(metrics['by_sentiment']['positive'], 1)
        self.assertEqual(metrics['by_sentiment']['neutral'], 1)
        self.assertEqual(metrics['by_sentiment']['negative'], 1)

    def test_get_metrics_empty(self):
        """Тест получения метрик когда нет данных"""
        # Удаляем файл если он существует
        import os
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        
        metrics = MetricsService.get_metrics()
        # Если файл не существует, _load_metrics возвращает пустой словарь
        # Но get_metrics должен вернуть структуру по умолчанию
        self.assertIsInstance(metrics, dict)

    def test_get_metrics_with_existing_data(self):
        """Тест получения метрик с существующими данными"""
        # Создаем файл с данными
        existing_data = {
            'total_submissions': 5,
            'by_sentiment': {'positive': 2, 'neutral': 3},
            'by_type': {'inquiry': 2, 'feedback': 3},
            'last_updated': '2024-01-01T00:00:00'
        }
        with open(settings.METRICS_FILE, 'w') as f:
            json.dump(existing_data, f)
        
        metrics = MetricsService.get_metrics()
        self.assertEqual(metrics['total_submissions'], 5)
        self.assertEqual(metrics['by_sentiment']['positive'], 2)
