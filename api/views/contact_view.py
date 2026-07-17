import logging
from rest_framework import status, viewsets
from rest_framework.response import Response
from api.models import ContactSubmission
from api.serializers import ContactSubmissionSerializer
from api.services import AIService, EmailService, RateLimitService, MetricsService

logger = logging.getLogger('api')

VALID_SENTIMENTS = frozenset({'positive', 'neutral', 'negative'})
VALID_REQUEST_TYPES = frozenset({
    'inquiry', 'feedback', 'collaboration', 'support', 'other',
})


class ContactView(viewsets.ModelViewSet):
    """
    API для обработки контактных форм
    POST /api/contact - создать новое обращение
    GET /api/contact - получить все обращения
    """

    queryset = ContactSubmission.objects.all()
    serializer_class = ContactSubmissionSerializer

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def create(self, request, *args, **kwargs):
        """
        Создает новое контактное обращение
        POST /api/contact
        """
        client_ip = self.get_client_ip(request)

        if not RateLimitService.is_allowed(client_ip):
            logger.warning(f"Превышен лимит запросов для IP: {client_ip}")
            return Response(
                {'error': 'Слишком много запросов. Пожалуйста, попробуйте позже.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Ошибка валидации: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            ai_service = AIService()
            comment = serializer.validated_data['comment']

            sentiment_result = ai_service.analyze_sentiment(comment)
            sentiment = sentiment_result.get('sentiment', 'neutral')
            if sentiment not in VALID_SENTIMENTS:
                sentiment = 'neutral'

            classification = ai_service.classify_request(comment)
            request_type = classification.get('type', 'other')
            if request_type not in VALID_REQUEST_TYPES:
                request_type = 'other'

            ai_response = ai_service.generate_response(
                serializer.validated_data['name'],
                comment
            )

            contact = serializer.save(
                sentiment=sentiment,
                request_type=request_type,
                ai_response=ai_response,
                ip_address=client_ip
            )

            logger.info(f"Создано новое обращение: {contact.id} для {contact.email}")

            email_data = {
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone,
                'comment': contact.comment,
                'sentiment': sentiment,
                'request_type': request_type,
            }

            EmailService.send_contact_confirmation(email_data)
            EmailService.send_admin_notification(email_data)

            MetricsService.record_submission({
                'sentiment': sentiment,
                'request_type': request_type,
            })

            return Response(
                {
                    'message': 'Спасибо! Ваше обращение успешно получено.',
                    'id': contact.id,
                    'sentiment': sentiment,
                    'request_type': request_type,
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Ошибка при создании обращения: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Не удалось обработать ваше обращение. Пожалуйста, попробуйте позже.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
