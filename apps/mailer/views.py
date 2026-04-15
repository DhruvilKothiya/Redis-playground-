from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .models import EmailRecord


from .serializers import BulkEmailSerializer
from .models import EmailBatch
from .tasks import send_bulk_email_task


class SendBulkEmailAPIView(APIView):
    def post(self, request):
        serializer = BulkEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        emails = serializer.validated_data["emails"]
        subject = serializer.validated_data["subject"]
        body = serializer.validated_data["body"]

        # Create batch before queuing
        batch = EmailBatch.objects.create(
            user=request.user,
            subject=subject,
            body=body,
            total_recipients=len(emails),
            success_count=0,
            failed_count=0,
        )

        records = [EmailRecord(batch=batch, email_address=email) for email in emails]
        EmailRecord.objects.bulk_create(records, batch_size=1000)

        transaction.on_commit(lambda: send_bulk_email_task.delay(batch.id))

        return Response(
            {
                "message": "Email batch queued successfully",
                "batch_id": batch.id,
                "total_recipients": len(emails),
                "success_count": batch.success_count,
            },
            status=status.HTTP_202_ACCEPTED,
        )