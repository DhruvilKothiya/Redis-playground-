from django.core.mail import EmailMessage, get_connection
from django.conf import settings
import concurrent.futures


class EmailService:
    @staticmethod
    def _send_single_email(batch, record, index, total_records):
        """Worker function that runs in a separate thread"""
        success = False
        error_msg = ""
        
        print(f"[{index}/{total_records}] Preparing to send sequence to: {record.email_address}")
        
        try:
            # Each thread must open its own secure connection to prevent SMTP stream corruption
            connection = get_connection(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                username=settings.EMAIL_HOST_USER,
                password=settings.EMAIL_HOST_PASSWORD,
                use_tls=settings.EMAIL_USE_TLS,
                timeout=getattr(settings, "EMAIL_TIMEOUT", 30),
            )
            
            msg = EmailMessage(
                subject=batch.subject,
                body=batch.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[record.email_address],
                connection=connection,
            )
            msg.send(fail_silently=False)
            
            # IMMEDIATELY update record
            record.status = True
            record.save(update_fields=["status"])
            success = True
            print(f"[{index}/{total_records}] Sent successfully\n")
            
        except Exception as e:
            # IMMEDIATELY update record
            record.status = False
            record.save(update_fields=["status"])
            error_msg = str(e)
            print(f"[{index}/{total_records}] Failed: {error_msg}\n")
            
        return record.id, success

    @staticmethod
    def process_bulk_batch(batch_id):
        from .models import EmailBatch, EmailRecord
        
        batch = EmailBatch.objects.get(id=batch_id)
        records = list(EmailRecord.objects.filter(batch=batch, status__isnull=True))
        total_records = len(records)
        
        success_ids = []
        failed_ids = []

        # We will use 10 concurrent threads to process emails 10x faster.
        # You can adjust `max_workers` depending on your server and SMTP provider limits.
        max_workers = 10 

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all email tasks to the thread pool
            futures = [
                executor.submit(EmailService._send_single_email, batch, record, index, total_records)
                for index, record in enumerate(records, start=1)
            ]
            
            # As threads complete, aggregate the results
            for future in concurrent.futures.as_completed(futures):
                record_id, success = future.result()
                if success:
                    success_ids.append(record_id)
                else:
                    failed_ids.append(record_id)

        return {
            "success_count": len(success_ids),
            "failed_count": len(failed_ids),
            "failed_emails": list(EmailRecord.objects.filter(id__in=failed_ids).values_list('email_address', flat=True))
        }