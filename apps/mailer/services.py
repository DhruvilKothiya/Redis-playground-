from django.core.mail import EmailMessage, get_connection
from django.conf import settings


class EmailService:
    @staticmethod
    def send_bulk_email(subject, body, recipient_list):
        success = 0
        failed = []

        connection = get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
        )

        connection.open()

        try:
            for email in recipient_list:
                try:
                    msg = EmailMessage(
                        subject=subject,
                        body=body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[email],
                        connection=connection,
                    )
                    msg.send(fail_silently=False)
                    success += 1
                except Exception:
                    failed.append(email)
        finally:
            connection.close()

        return {
            "success_count": success,
            "failed_count": len(failed),
            "failed_emails": failed,
        }