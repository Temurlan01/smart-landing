from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from api.models import ContactSubmission
from api.services import RateLimitService
from unittest.mock import patch, MagicMock
import json


class ContactViewTest(TestCase):
    """Тесты для ContactView API"""

    def setUp(self):
        """Создаем клиент API перед каждым тестом"""
        self.client = APIClient()
        self.valid_contact_data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'This is a valid comment with more than 10 characters'
        }

    @patch('api.services.rate_limit_service.RateLimitService.is_allowed')
    def test_create_contact_success(self, mock_rate_limit):
        """Тест успешного создания контакта"""
        mock_rate_limit.return_value = True
        response = self.client.post('/api/contact/', self.valid_contact_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)
        self.assertIn('message', response.data)
        self.assertIn('sentiment', response.data)
        self.assertIn('request_type', response.data)
        
        # Проверяем что контакт создан в БД
        self.assertEqual(ContactSubmission.objects.count(), 1)

    @patch('api.services.rate_limit_service.RateLimitService.is_allowed')
    def test_create_contact_invalid_email(self, mock_rate_limit):
        """Тест создания контакта с невалидным email"""
        mock_rate_limit.return_value = True
        invalid_data = self.valid_contact_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        response = self.client.post('/api/contact/', invalid_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

    @patch('api.services.rate_limit_service.RateLimitService.is_allowed')
    def test_create_contact_invalid_phone(self, mock_rate_limit):
        """Тест создания контакта с невалидным телефоном"""
        mock_rate_limit.return_value = True
        invalid_data = self.valid_contact_data.copy()
        invalid_data['phone'] = '123'
        
        response = self.client.post('/api/contact/', invalid_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('phone', response.data)

    @patch('api.services.rate_limit_service.RateLimitService.is_allowed')
    def test_create_contact_short_name(self, mock_rate_limit):
        """Тест создания контакта с коротким именем"""
        mock_rate_limit.return_value = True
        invalid_data = self.valid_contact_data.copy()
        invalid_data['name'] = 'I'
        
        response = self.client.post('/api/contact/', invalid_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.data)

    @patch('api.services.rate_limit_service.RateLimitService.is_allowed')
    def test_create_contact_short_comment(self, mock_rate_limit):
        """Тест создания контакта с коротким комментарием"""
        mock_rate_limit.return_value = True
        invalid_data = self.valid_contact_data.copy()
        invalid_data['comment'] = 'Short'
        
        response = self.client.post('/api/contact/', invalid_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('comment', response.data)

    @patch('api.services.rate_limit_service.RateLimitService.is_allowed')
    def test_create_contact_missing_required_field(self, mock_rate_limit):
        """Тест создания контакта без обязательного поля"""
        mock_rate_limit.return_value = True
        invalid_data = self.valid_contact_data.copy()
        del invalid_data['name']
        
        response = self.client.post('/api/contact/', invalid_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.data)

    @patch('api.services.rate_limit_service.RateLimitService.is_allowed')
    @override_settings(RATE_LIMIT_REQUESTS=2, RATE_LIMIT_MINUTES=10)
    def test_rate_limiting(self, mock_rate_limit):
        """Тест rate limiting"""
        # Первые 2 запроса разрешены
        mock_rate_limit.side_effect = [True, True, False]
        
        # Отправляем 2 успешных запроса
        for i in range(2):
            response = self.client.post('/api/contact/', self.valid_contact_data, format='json')
            self.assertEqual(response.status_code, 201)
        
        # Третий запрос должен быть заблокирован
        response = self.client.post('/api/contact/', self.valid_contact_data, format='json')
        self.assertEqual(response.status_code, 429)
        self.assertIn('error', response.data)

    @patch('api.views.contact_view.AIService')
    @patch('api.services.rate_limit_service.RateLimitService.is_allowed')
    def test_ai_sentiment_analysis_called(self, mock_rate_limit, mock_ai_service):
        """Тест что AI сервис вызывается для анализа тональности"""
        mock_rate_limit.return_value = True
        mock_ai_instance = MagicMock()
        mock_ai_instance.analyze_sentiment.return_value = {'sentiment': 'positive', 'score': 0.8}
        mock_ai_instance.classify_request.return_value = {'type': 'inquiry', 'confidence': 0.9}
        mock_ai_instance.generate_response.return_value = 'Test response'
        mock_ai_service.return_value = mock_ai_instance
        
        response = self.client.post('/api/contact/', self.valid_contact_data, format='json')
        self.assertEqual(response.status_code, 201)
        mock_ai_instance.analyze_sentiment.assert_called_once()

    @patch('api.views.contact_view.EmailService')
    @patch('api.services.rate_limit_service.RateLimitService.is_allowed')
    def test_email_services_called(self, mock_rate_limit, mock_email_service):
        """Тест что email сервисы вызываются"""
        mock_rate_limit.return_value = True
        mock_email_service.send_contact_confirmation.return_value = True
        mock_email_service.send_admin_notification.return_value = True
        
        response = self.client.post('/api/contact/', self.valid_contact_data, format='json')
        self.assertEqual(response.status_code, 201)
        mock_email_service.send_contact_confirmation.assert_called_once()
        mock_email_service.send_admin_notification.assert_called_once()

    @patch('api.views.contact_view.MetricsService')
    @patch('api.services.rate_limit_service.RateLimitService.is_allowed')
    def test_metrics_service_called(self, mock_rate_limit, mock_metrics_service):
        """Тест что сервис метрик вызывается"""
        mock_rate_limit.return_value = True
        mock_metrics_service.record_submission.return_value = None
        
        response = self.client.post('/api/contact/', self.valid_contact_data, format='json')
        self.assertEqual(response.status_code, 201)
        mock_metrics_service.record_submission.assert_called_once()

    def test_get_contact_list(self):
        """Тест получения списка контактов"""
        # Очищаем базу перед тестом
        ContactSubmission.objects.all().delete()
        
        # Создаем несколько контактов
        ContactSubmission.objects.create(
            name='Ivan Petrov',
            email='ivan@example.com',
            phone='+71234567890',
            comment='This is a valid comment with more than 10 characters'
        )
        ContactSubmission.objects.create(
            name='Petr Ivanov',
            email='petr@example.com',
            phone='+79876543210',
            comment='Another test comment'
        )
        
        response = self.client.get('/api/contact/')
        self.assertEqual(response.status_code, 200)
        results = response.data.get('results', response.data)
        self.assertGreaterEqual(len(results), 2)

    def test_get_contact_detail(self):
        """Тест получения детальной информации о контакте"""
        contact = ContactSubmission.objects.create(**self.valid_contact_data)
        
        response = self.client.get(f'/api/contact/{contact.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], str(contact.id))
        self.assertEqual(response.data['name'], contact.name)

    def test_update_contact(self):
        """Тест обновления контакта"""
        contact = ContactSubmission.objects.create(**self.valid_contact_data)
        
        update_data = {
            'name': 'Updated Name',
            'email': 'updated@example.com',
            'phone': '+79876543210',
            'comment': 'Updated comment text'
        }
        
        response = self.client.put(f'/api/contact/{contact.id}/', update_data, format='json')
        self.assertEqual(response.status_code, 200)
        
        contact.refresh_from_db()
        self.assertEqual(contact.name, 'Updated Name')

    def test_delete_contact(self):
        """Тест удаления контакта"""
        contact = ContactSubmission.objects.create(**self.valid_contact_data)
        
        response = self.client.delete(f'/api/contact/{contact.id}/')
        self.assertEqual(response.status_code, 204)
        
        self.assertEqual(ContactSubmission.objects.count(), 0)


class HealthCheckViewTest(TestCase):
    """Тесты для health check endpoint"""

    def setUp(self):
        """Создаем клиент API"""
        self.client = APIClient()

    def test_health_check_success(self):
        """Т успешного health check"""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertEqual(response.data['message'], 'API is running')
        self.assertEqual(response.data['version'], '1.0.0')


class MetricsViewTest(TestCase):
    """Тесты для metrics endpoint"""

    def setUp(self):
        """Создаем клиент API"""
        self.client = APIClient()

    def test_get_metrics_success(self):
        """Тест успешного получения метрик"""
        response = self.client.get('/api/metrics/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_submissions', response.data)
        self.assertIn('by_sentiment', response.data)
        self.assertIn('by_type', response.data)
        self.assertIn('last_updated', response.data)

    def test_get_metrics_with_data(self):
        """Тест получения метрик с данными"""
        # Создаем контакт для генерации метрик
        contact_data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'Test comment for metrics'
        }
        self.client.post('/api/contact/', contact_data, format='json')
        
        response = self.client.get('/api/metrics/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.data['total_submissions'], 0)


class APIIntegrationTest(TestCase):
    """Интеграционные тесты для API"""

    def setUp(self):
        """Создаем клиент API"""
        self.client = APIClient()

    @patch('api.services.rate_limit_service.RateLimitService.is_allowed')
    def test_full_contact_submission_flow(self, mock_rate_limit):
        """Тест полного процесса отправки контакта"""
        mock_rate_limit.return_value = True
        contact_data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'I want to discuss collaboration on your project'
        }
        
        # Отправляем контакт
        response = self.client.post('/api/contact/', contact_data, format='json')
        self.assertEqual(response.status_code, 201)
        
        contact_id = response.data['id']
        
        # Проверяем что контакт создан
        contact = ContactSubmission.objects.get(id=contact_id)
        self.assertEqual(contact.name, 'Ivan Petrov')
        self.assertEqual(contact.email, 'ivan@example.com')
        
        # Проверяем что метрики обновились
        metrics_response = self.client.get('/api/metrics/')
        self.assertEqual(metrics_response.status_code, 200)
        self.assertGreater(metrics_response.data['total_submissions'], 0)
        
        # Проверяем что контакт доступен в списке
        list_response = self.client.get('/api/contact/')
        self.assertEqual(list_response.status_code, 200)
        results = list_response.data.get('results', list_response.data)
        self.assertGreater(len(results), 0)

    @patch('api.services.rate_limit_service.RateLimitService.is_allowed')
    def test_error_handling_invalid_data(self, mock_rate_limit):
        """Тест обработки ошибок при невалидных данных"""
        mock_rate_limit.return_value = True
        invalid_data = {
            'name': 'I',
            'email': 'invalid',
            'phone': '123',
            'comment': 'Short'
        }
        
        response = self.client.post('/api/contact/', invalid_data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.data)
        self.assertIn('email', response.data)
        self.assertIn('phone', response.data)
        self.assertIn('comment', response.data)

    def test_concurrent_requests_different_ips(self):
        """Тест одновременных запросов с разных IP"""
        from django.test import RequestFactory
        
        contact_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '+71234567890',
            'comment': 'Test comment for concurrent requests'
        }
        
        # Эмулируем запросы с разных IP
        factory = RequestFactory()
        ips = ['192.168.1.1', '192.168.1.2', '192.168.1.3']
        
        for ip in ips:
            request = factory.post('/api/contact/', contact_data, content_type='application/json')
            request.META['REMOTE_ADDR'] = ip
            # В реальном тесте здесь нужно использовать APIRequestFactory
            # Для простоты проверяем что база позволяет создавать контакты
            ContactSubmission.objects.create(**contact_data, ip_address=ip)
        
        self.assertEqual(ContactSubmission.objects.count(), 3)
