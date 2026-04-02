from celery import shared_task
from .services import EmailService
from .models import EmailBatch


@shared_task(bind=True, max_retries=3)
def send_bulk_email_task(self, batch_id):
    try:
        # Send emails incrementally using real-time database updates
        result = EmailService.process_bulk_batch(batch_id)
        
        # Update overall batch stats
        batch = EmailBatch.objects.get(id=batch_id)
        batch.success_count = result["success_count"]
        batch.failed_count = result["failed_count"]
        batch.save()
        
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
