from django.db import models
from django.core.validators import EmailValidator, RegexValidator
import uuid

class ContactSubmission(models.Model):
    """Модель для хранения контактных данных"""

    SENTIMENT_CHOICES = [
        ('positive', 'Положительный'),
        ('neutral', 'Нейтральный'),
        ('negative', 'Отрицательный'),
    ]

    REQUEST_TYPE_CHOICES = [
        ('inquiry', 'Запрос'),
        ('feedback', 'Отзыв'),
        ('collaboration', 'Сотрудничество'),
        ('support', 'Поддержка'),
        ('other', 'Другое'),
    ]
    REQUEST_TYPE_CHOICES = [
        ('inquiry', 'Запрос'),
        ('feedback', 'Отзыв'),
        ('collaboration', 'Сотрудничество'),
        ('support', 'Поддержка'),
        ('other', 'Другое'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Номер телефона должен содержать 9-15 цифр',
                code='invalid_phone'
            )
        ]
    )
    comment = models.TextField()

    sentiment = models.CharField(
        max_length=10,
        choices=SENTIMENT_CHOICES,
        null=True,
        blank=True,
    )
    ai_response = models.TextField(null=True, blank=True)
    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPE_CHOICES,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Отправка контактных данных'
        verbose_name_plural = 'Отправки контактных данных'

    def __str__(self):
        return f"{self.name} - {self.email}"