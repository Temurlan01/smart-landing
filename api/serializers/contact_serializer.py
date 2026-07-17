from rest_framework import serializers
from api.models import ContactSubmission
from django.core.validators import EmailValidator, RegexValidator
import re

class ContactSubmissionSerializer(serializers.ModelSerializer):
    """Сериализатор для контактной формы с валидацией"""

    email = serializers.EmailField(validators=[EmailValidator()])
    phone = serializers.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Номер телефона должен содержать 9-15 цифр'
            )
        ]
    )

    class Meta:
        model = ContactSubmission
        fields = ['id',
                  'name',
                  'email',
                  'phone',
                  'comment',
                  'sentiment',
                  'ai_response',
                  'request_type',
                  'created_at'
                  ]
        read_only_fields = [
            'id',
            'sentiment',
            'ai_response',
            'request_type',
            'created_at'
        ]

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Имя должно содержать минимум 2 символа")
        if not all(c.isalpha() or c.isspace() for c in value):
            raise serializers.ValidationError("Имя должно содержать только буквы и пробелы")
        return value.strip()

    def validate_comment(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Комментарий должен содержать минимум 10 символов")
        if len(value) > 5000:
            raise serializers.ValidationError("Комментарий не должен превышать 5000 символов")
        return value.strip()

    def validate_phone(self, value):
        cleaned = re.sub(r'[^\d+]', '', value)
        if not cleaned or len(cleaned) < 9:
            raise serializers.ValidationError("Недействительный номер телефона")
        return value