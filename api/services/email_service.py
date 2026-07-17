import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger('api')

class EmailService:
    """Сервис для отправки email-уведомлений"""

    @staticmethod
    def send_contact_confirmation(contact_data: dict) -> bool:
        """
        Отправляет письмо подтверждения пользователю
        """
        try:
            subject = "Мы получили ваше сообщение"
            message = f"""Здравствуйте {contact_data['name']},
            Спасибо за ваше обращение! Мы получили ваше 
            сообщение и ответим вам в ближайшее время.
            
            Ваши контактные данные:
            - Email: {contact_data['email']}
            - Телефон: {contact_data['phone']}

            Текст сообщения:{contact_data['comment']} 
            С уважением,Команда разработчиков """

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contact_data['email']],
                fail_silently=False,
            )

            logger.info(
                f"Письмо с подтверждением отправлено на {contact_data['email']}\n"
                f"Subject: {subject}\n{message}"
            )
            return True

        except Exception as e:
            logger.error(f"Не удалось отправить письмо пользователю  {contact_data['email']}: {str(e)}")
            return False

    @staticmethod
    def send_admin_notification(contact_data: dict) -> bool:
        """
        Отправляет уведомление админу о новом обращении
        """
        try:
            subject = f"Новое обращение {contact_data['name']}"
            message = f"""Новое обращение получено:
            
            Имя: {contact_data['name']}
            Email: {contact_data['email']}
            Телефон: {contact_data['phone']}
            
            Сообщение:
            {contact_data['comment']}
            
            Тональность: {contact_data.get('sentiment', 'Не определена')}
            Тип обращения: {contact_data.get('request_type', 'Не определён')}
            """

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )

            logger.info(
                f"Администратор уведомлён о новом обращении от {contact_data['name']}\n"
                f"Subject: {subject}\n{message}"
            )
            return True

        except Exception as e:
            logger.error(f"Не удалось отправить уведомление администратору: {str(e)}")
            return False