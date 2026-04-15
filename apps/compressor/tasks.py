import tempfile
import os
from celery import shared_task
from pathlib import Path
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from celery.utils.log import get_task_logger
from .models import CompressionJob


logger = get_task_logger(__name__)
from .services import compress_pdf

@shared_task(bind=True)
def compress_pdf_task(self, job_id):
    try:
        job = CompressionJob.objects.get(id=job_id)
        logger.info(f"\033[33mFound job with ID: {job_id} for file: {job.original_file.name}\033[0m")
        job.status = "PROCESSING"
        logger.info(f"\033[33mUpdated job status to PROCESSING for Job ID: {job_id}\033[0m")
        job.save()

        logger.info(f"\033[33mStarting processing for file: {job.original_file.name} (Job ID: {job_id})\033[0m")
        input_path = job.original_file.path
        logger.info(f"\033[33mCompressing file at path: {input_path} for Job ID: {job_id}\033[0m")

        # Compress to a temporary file so Django can handle the final save without duplicates
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
            temp_path = temp_file.name

        logger.info(f"\033[33mCreated temporary file for compression: {temp_path} for Job ID: {job_id}\033[0m")

        try:
            compress_pdf(input_path , temp_path)
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
        
        logger.info(f"\033[33mFinished processing and successfully compressed file for Job ID: {job_id}. Output saved as: {job.compressed_file.name}\033[0m")

    except ObjectDoesNotExist:
        logger.warning(f"CompressionJob with id {job_id} does not exist. Aborting task.")
        return
    except Exception as e:
        if 'job' in locals():
            job.status = "FAILED"
            job.save()
        logger.error(f"Failed to compress PDF for job {job_id}: {str(e)}", exc_info=True)
        raise e