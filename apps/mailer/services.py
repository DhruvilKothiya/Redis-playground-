from django.core.mail import EmailMessage, get_connection
from django.conf import settings


class EmailService:
    @staticmethod
    def process_bulk_batch(batch_id):
        from .models import EmailBatch, EmailRecord
        
        batch = EmailBatch.objects.get(id=batch_id)
        records = EmailRecord.objects.filter(batch=batch, status__isnull=True)
        
        success_ids = []
        failed_ids = []

        connection = get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
        )

        connection.open()

        try:
            total_records = len(records)
            for index, record in enumerate(records, start=1):
                print(f"[{index}/{total_records}] Sending email to {record.email_address}...")
                try:
                    msg = EmailMessage(
                        subject=batch.subject,
                        body=batch.body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[record.email_address],
                        connection=connection,
                    )
                    msg.send(fail_silently=False)
                    success_ids.append(record.id)
                    print(f"[{index}/{total_records}] Sent successfully\n")
                except Exception as e:
                    failed_ids.append(record.id)
                    print(f"[{index}/{total_records}] Failed: {str(e)}\n")
        finally:
            connection.close()
            
        # Bulk update statuses
        if success_ids:
            EmailRecord.objects.filter(id__in=success_ids).update(status=True)
        if failed_ids:
            EmailRecord.objects.filter(id__in=failed_ids).update(status=False)

        return {
            "success_count": len(success_ids),
            "failed_count": len(failed_ids),
            "failed_emails": list(EmailRecord.objects.filter(id__in=failed_ids).values_list('email_address', flat=True))
        }