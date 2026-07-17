from django.test import TestCase
from api.serializers import ContactSubmissionSerializer
from api.models import ContactSubmission
import uuid


class ContactSubmissionSerializerTest(TestCase):
    """Тесты для сериализатора ContactSubmission"""

    def test_valid_contact_data(self):
        """Тест валидных данных контакта"""
        data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'This is a valid comment with more than 10 characters'
        }
        serializer = ContactSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
    def test_invalid_email(self):
        """Тест невалидного email"""
        data = {
            'name': 'Ivan Petrov',
            'email': 'invalid-email',
            'phone': '+71234567890',
            'comment': 'This is a valid comment with more than 10 characters'
        }
        serializer = ContactSubmissionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_invalid_phone_too_short(self):
        """Тест слишком короткого номера телефона"""
        data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': '123',
            'comment': 'This is a valid comment with more than 10 characters'
        }
        serializer = ContactSubmissionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone', serializer.errors)

    def test_invalid_phone_format(self):
        """Тест невалидного формата телефона"""
        data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': 'abc-def-ghi',
            'comment': 'This is a valid comment with more than 10 characters'
        }
        serializer = ContactSubmissionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone', serializer.errors)

    def test_name_too_short(self):
        """Тест слишком короткого имени"""
        data = {
            'name': 'I',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'This is a valid comment with more than 10 characters'
        }
        serializer = ContactSubmissionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_name_with_numbers(self):
        """Тест имени с цифрами (недопустимо)"""
        data = {
            'name': 'Ivan123',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'This is a valid comment with more than 10 characters'
        }
        serializer = ContactSubmissionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_comment_too_short(self):
        """Тест слишком короткого комментария"""
        data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'Short'
        }
        serializer = ContactSubmissionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('comment', serializer.errors)

    def test_comment_too_long(self):
        """Тест слишком длинного комментария"""
        data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'a' * 5001
        }
        serializer = ContactSubmissionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('comment', serializer.errors)

    def test_name_whitespace_stripping(self):
        """Тест удаления пробелов в начале и конце имени"""
        data = {
            'name': '  Ivan Petrov  ',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'This is a valid comment with more than 10 characters'
        }
        serializer = ContactSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        contact = serializer.save()
        self.assertEqual(contact.name, 'Ivan Petrov')

    def test_comment_whitespace_stripping(self):
        """Тест удаления пробелов в начале и конце комментария"""
        data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': '  This is a valid comment with more than 10 characters  '
        }
        serializer = ContactSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        contact = serializer.save()
        self.assertEqual(contact.comment, 'This is a valid comment with more than 10 characters')

    def test_read_only_fields(self):
        """Тест что read-only поля нельзя изменить через сериализатор"""
        contact = ContactSubmission.objects.create(
            name='Ivan Petrov',
            email='ivan@example.com',
            phone='+71234567890',
            comment='Test comment'
        )
        data = {
            'name': 'Updated Name',
            'email': 'updated@example.com',
            'phone': '+79876543210',
            'comment': 'Updated comment',
            'sentiment': 'positive',
            'request_type': 'feedback'
        }
        serializer = ContactSubmissionSerializer(contact, data=data)
        self.assertTrue(serializer.is_valid())
        updated_contact = serializer.save()
        self.assertIsNone(updated_contact.sentiment)
        self.assertIsNone(updated_contact.request_type)

    def test_phone_with_special_chars(self):
        """Тест телефона с разрешенными специальными символами"""
        data = {
            'name': 'Ivan Petrov',
            'email': 'ivan@example.com',
            'phone': '+15551234567',
            'comment': 'This is a valid comment with more than 10 characters'
        }
        serializer = ContactSubmissionSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_required_field(self):
        """Тест отсутствия обязательного поля"""
        data = {
            'email': 'ivan@example.com',
            'phone': '+71234567890',
            'comment': 'This is a valid comment with more than 10 characters'
        }
        serializer = ContactSubmissionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
