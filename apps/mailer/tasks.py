from celery import shared_task
from .services import EmailService
from .models import EmailBatch


@shared_task(bind=True, max_retries=3)
def send_bulk_email_task(self, batch_id):
    try:
 
        result = EmailService.process_bulk_batch(batch_id)
        
        # Update overall batch stats
        # ... the result contains the counts, but process_bulk_batch might already update the DB if we want, or we can keep it here.
        # Actually, let's keep database updates for batch counts centralized in process_bulk_batch or keep it here.
        # process_bulk_batch can return the dictionary as before.
        batch = EmailBatch.objects.get(id=batch_id)
        batch.success_count = result["success_count"]
        batch.failed_count = result["failed_count"]
        batch.save()
        
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
