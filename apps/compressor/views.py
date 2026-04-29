from celery import chord
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    CompressionUploadSerializer,
    CompressionJobSerializer,
    CompressionBatchSerializer,
)
from .models import CompressionJob, CompressionBatch
from .tasks import compress_pdf_task, batch_complete_callback


class UploadAndCompressAPIView(APIView):
    def post(self, request):
        serializer = CompressionUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        files = serializer.validated_data["files"]

        with transaction.atomic():
            # Create the parent batch record
            batch = CompressionBatch.objects.create(
                total_jobs=len(files),
                status="PENDING",
            )

            # Create one DB job row per uploaded PDF, linked to the batch
            jobs = [
                CompressionJob.objects.create(original_file=file, batch=batch)
                for file in files
            ]

            # Build and dispatch the chord only after DB commit
            def dispatch_chord():
                # Header: all individual compression tasks run in parallel
                header = [compress_pdf_task.s(job.id) for job in jobs]

                # Callback: fires once every header task finishes
                # .s(batch.id) passes batch_id as the second argument after job_results
                callback = batch_complete_callback.s(batch.id)

                chord(header)(callback)

            transaction.on_commit(dispatch_chord)

        return Response(
            {
                "message": "Compression batch started successfully",
                "batch_id": batch.id,
                "total_jobs": batch.total_jobs,
                "jobs": CompressionJobSerializer(jobs, many=True).data,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class BatchStatusAPIView(APIView):
    def get(self, request, batch_id):
        try:
            batch = CompressionBatch.objects.prefetch_related("jobs").get(id=batch_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": f"Batch {batch_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            CompressionBatchSerializer(batch).data,
            status=status.HTTP_200_OK,
        )


class CompressionStatusAPIView(APIView):
    def get(self, request, job_id):
        try:
            job = CompressionJob.objects.get(id=job_id)
        except ObjectDoesNotExist:
            return Response(
                {"error": f"Job {job_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            CompressionJobSerializer(job).data,
            status=status.HTTP_200_OK,
        )
