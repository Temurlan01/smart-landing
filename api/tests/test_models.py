from django.test import TestCase
from api.models import ContactSubmission
import uuid


class ContactSubmissionModelTest(TestCase):
    """Тесты для модели ContactSubmission"""

    def setUp(self):
        """Создаем тестовый контакт перед каждым тестом"""
        self.contact = ContactSubmission.objects.create(
            name="Ivan Petrov",
            email="ivan@example.com",
            phone="+71234567890",
            comment="Test comment for testing purposes",
            sentiment="neutral",
            request_type="inquiry",
            ip_address="127.0.0.1"
        )

    def test_contact_creation(self):
        """Тест создания контакта"""
        self.assertEqual(self.contact.name, "Ivan Petrov")
        self.assertEqual(self.contact.email, "ivan@example.com")
        self.assertEqual(self.contact.phone, "+71234567890")
        self.assertEqual(self.contact.sentiment, "neutral")
        self.assertEqual(self.contact.request_type, "inquiry")

    def test_contact_id_is_uuid(self):
        """Тест что ID является UUID"""
        self.assertIsInstance(self.contact.id, uuid.UUID)

    def test_contact_str_representation(self):
        """Тест строкового представления"""
        expected = f"{self.contact.name} - {self.contact.email}"
        self.assertEqual(str(self.contact), expected)

    def test_contact_ordering(self):
        """Тест сортировки по created_at (по убыванию)"""
        contact2 = ContactSubmission.objects.create(
            name="Petr Ivanov",
            email="petr@example.com",
            phone="+79876543210",
            comment="Another test comment"
        )
        contacts = ContactSubmission.objects.all()
        self.assertEqual(contacts[0], contact2)
        self.assertEqual(contacts[1], self.contact)

    def test_sentiment_choices(self):
        """Тест допустимых значений sentiment"""
        valid_sentiments = ['positive', 'neutral', 'negative']
        for sentiment in valid_sentiments:
            contact = ContactSubmission.objects.create(
                name="Test User",
                email="test@example.com",
                phone="+71234567890",
                comment="Test comment",
                sentiment=sentiment
            )
            self.assertEqual(contact.sentiment, sentiment)

    def test_request_type_choices(self):
        """Тест допустимых значений request_type"""
        valid_types = ['inquiry', 'feedback', 'collaboration', 'support', 'other']
        for req_type in valid_types:
            contact = ContactSubmission.objects.create(
                name="Test User",
                email="test@example.com",
                phone="+71234567890",
                comment="Test comment",
                request_type=req_type
            )
            self.assertEqual(contact.request_type, req_type)

    def test_contact_without_optional_fields(self):
        """Тест создания контакта без опциональных полей"""
        contact = ContactSubmission.objects.create(
            name="Simple User",
            email="simple@example.com",
            phone="+71234567890",
            comment="Simple comment"
        )
        self.assertIsNone(contact.sentiment)
        self.assertIsNone(contact.request_type)
        self.assertIsNone(contact.ai_response)
        self.assertIsNone(contact.ip_address)

    def test_updated_at_auto_update(self):
        """Тест автоматического обновления updated_at"""
        original_updated_at = self.contact.updated_at
        self.contact.name = "Updated Name"
        self.contact.save()
        self.assertGreater(self.contact.updated_at, original_updated_at)
