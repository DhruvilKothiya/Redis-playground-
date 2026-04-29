import tempfile
import os
from celery import shared_task
from pathlib import Path
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from celery.utils.log import get_task_logger
from .models import CompressionJob, CompressionBatch
from .services import compress_pdf

logger = get_task_logger(__name__)


@shared_task(bind=True)
def compress_pdf_task(self, job_id):
    try:
        job = CompressionJob.objects.get(id=job_id)
        logger.info(f"\033[33mFound job with ID: {job_id} for file: {job.original_file.name}\033[0m")
        job.status = "PROCESSING"
        job.save()
        logger.info(f"\033[33mUpdated job status to PROCESSING for Job ID: {job_id}\033[0m")

        input_path = job.original_file.path
        logger.info(f"\033[33mCompressing file at path: {input_path} for Job ID: {job_id}\033[0m")

        # Compress to a temporary file so Django can handle the final save without duplicates
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_path = temp_file.name

        logger.info(f"\033[33mCreated temporary file for compression: {temp_path} for Job ID: {job_id}\033[0m")

        try:
            compress_pdf(input_path, temp_path)
            logger.info(f"\033[33mSuccessfully compressed file for Job ID: {job_id}\033[0m")

            with open(temp_path, "rb") as f:
                job.compressed_file.save(Path(input_path).name, File(f), save=False)
            logger.info(f"\033[33mSaved compressed file for Job ID: {job_id}\033[0m")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info(f"\033[33mRemoved temporary file: {temp_path} for Job ID: {job_id}\033[0m")

        job.status = "COMPLETED"
        job.save()

        logger.info(
            f"\033[33mFinished processing and successfully compressed file for Job ID: {job_id}. "
            f"Output saved as: {job.compressed_file.name}\033[0m"
        )

        # Return result dict — chord callback receives a list of these
        return {"job_id": job_id, "status": "COMPLETED"}

    except ObjectDoesNotExist:
        logger.warning(f"CompressionJob with id {job_id} does not exist. Aborting task.")
        return {"job_id": job_id, "status": "NOT_FOUND"}

    except Exception as e:
        if "job" in locals():
            job.status = "FAILED"
            job.save()
        logger.error(f"Failed to compress PDF for job {job_id}: {str(e)}", exc_info=True)
        # Return instead of raise so the chord callback still fires even on failure
        return {"job_id": job_id, "status": "FAILED"}


@shared_task(bind=True)
def batch_complete_callback(self, job_results, batch_id):
    """
    Chord callback — fires automatically once ALL compress_pdf_task jobs finish.

    job_results: list of dicts returned by each compress_pdf_task
                 e.g. [{"job_id": 1, "status": "COMPLETED"}, {"job_id": 2, "status": "FAILED"}, ...]
    batch_id:    the CompressionBatch PK, passed via chord(...).si() immutable signature
    """
    try:
        batch = CompressionBatch.objects.get(id=batch_id)
    except ObjectDoesNotExist:
        logger.warning(f"CompressionBatch with id {batch_id} does not exist. Aborting callback.")
        return

    logger.info(f"\033[36mChord callback fired for Batch ID: {batch_id} with {len(job_results)} results\033[0m")

    completed = sum(1 for r in job_results if r and r.get("status") == "COMPLETED")
    failed = sum(1 for r in job_results if r and r.get("status") != "COMPLETED")

    batch.completed_jobs = completed
    batch.failed_jobs = failed
    batch.completed_at = timezone.now()

    if failed == 0:
        batch.status = "COMPLETED"
    elif completed == 0:
        batch.status = "FAILED"
    else:
        batch.status = "PARTIAL_FAILURE"

    batch.save()

    logger.info(
        f"\033[36mBatch {batch_id} finalised — status: {batch.status}, "
        f"completed: {completed}, failed: {failed}\033[0m"
    )
