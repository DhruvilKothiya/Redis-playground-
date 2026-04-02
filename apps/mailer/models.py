from django.db import models
from django.conf import settings


class EmailBatch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_batches")
    subject = models.CharField(max_length=255)
    body = models.TextField()
    total_recipients = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Batch {self.id} - {self.subject}"


class EmailRecord(models.Model):
    batch = models.ForeignKey(EmailBatch, on_delete=models.CASCADE, related_name="email_records")
    email_address = models.EmailField()
    status = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="True=Sent, False=Failed, None=Pending"
    )

    def __str__(self):
        return f"{self.email_address} - Batch {self.batch.id}"