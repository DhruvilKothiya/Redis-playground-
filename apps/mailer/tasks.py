from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from celery.utils.log import get_task_logger
from .services import EmailService
from .models import EmailBatch

logger = get_task_logger(__name__)



@shared_task(bind=True, max_retries=3)
def send_bulk_email_task(self, batch_id):
    try:
 
        result = EmailService.process_bulk_batch(batch_id)
        batch = EmailBatch.objects.get(id=batch_id)
        batch.success_count = result["success_count"]
        batch.failed_count = result["failed_count"]
        batch.save()
        
        return result
    except ObjectDoesNotExist:
        logger.warning(f"EmailBatch with id {batch_id} does not exist. It may have been deleted. Aborting task without retry.")
        return None
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
