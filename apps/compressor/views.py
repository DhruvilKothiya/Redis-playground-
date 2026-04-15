from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .serializers import CompressionUploadSerializer, CompressionJobSerializer
from .models import CompressionJob
from .tasks import compress_pdf_task


class UploadAndCompressAPIView(APIView):
    def post(self, request):
        serializer = CompressionUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        files = serializer.validated_data["files"]
        jobs = []

        with transaction.atomic():
            for file in files:
                job = CompressionJob.objects.create(original_file=file)
                transaction.on_commit(lambda j=job: compress_pdf_task.delay(j.id))
                jobs.append(job)

        return Response({
            "message": "Compression started",
            "jobs": CompressionJobSerializer(jobs, many=True).data
        }, status=status.HTTP_202_ACCEPTED)


class CompressionStatusAPIView(APIView):
    def get(self, request, job_id):
        job = CompressionJob.objects.get(id=job_id)
        return Response(CompressionJobSerializer(job).data)