from django.core.mail import EmailMessage, get_connection
from django.conf import settings
import concurrent.futures
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class EmailService:
    @staticmethod
    def _send_single_email(batch, record, index, total):
        """Worker function that runs in a separate thread"""
        try:
            logger.info(f"[{index}/{total}] Preparing to send email to: {record.email_address}")
            
            # Use context manager for proper connection handling
            with get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS,
                timeout=getattr(settings, "EMAIL_TIMEOUT", 30),
            ) as connection:
                msg = EmailMessage(
                    subject=batch.subject,
                    body=batch.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[record.email_address],
                    connection=connection,
                )
                msg.send(fail_silently=False)
            
            record.status = True
            record.save(update_fields=["status"])
            logger.info(f"[{index}/{total}] Successfully sent email to: {record.email_address}")
            return record.id, True
            
        except Exception as e:
            record.status = False
            record.save(update_fields=["status"])
            logger.error(f"[{index}/{total}] Failed to send email to {record.email_address}: {str(e)}", exc_info=True)
            return record.id, False

    @staticmethod
    def process_bulk_batch(batch_id):
        from .models import EmailBatch, EmailRecord
        
        batch = EmailBatch.objects.get(id=batch_id)
        records = list(EmailRecord.objects.filter(batch=batch, status__isnull=True))
        total = len(records)
        
        success_ids, failed_ids = [], []

        # Simple thread pool execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(EmailService._send_single_email, batch, record, idx, total)
                for idx, record in enumerate(records, start=1)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                record_id, success = future.result()
                if success:
                    success_ids.append(record_id)
                else:
                    failed_ids.append(record_id)

        failed_emails = EmailRecord.objects.filter(id__in=failed_ids).values_list('email_address', flat=True)

        return {
            "success_count": len(success_ids),
            "failed_count": len(failed_ids),
            "failed_emails": list(failed_emails)
        }