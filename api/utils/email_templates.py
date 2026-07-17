def user_confirmation_template(name: str, email: str, phone: str, comment: str) -> (str, str):
    subject = "We received your message"
    body = f"""Hello {name},

Thank you for contacting me. I received your message and will respond shortly.

Contact:
- Email: {email}
- Phone: {phone}

Message:
{comment}

Best regards,
Developer
"""
    return subject, body

def admin_notification_template(data: dict) -> (str, str):
    subject = f"New contact from {data.get('name')}"
    body = f"""
New contact:
Name: {data.get('name')}
Email: {data.get('email')}
Phone: {data.get('phone')}

Comment:
{data.get('comment')}
"""
    return subject, body