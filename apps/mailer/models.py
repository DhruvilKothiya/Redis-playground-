from django.db import models


class EmailBatch(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    total_recipients = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Batch {self.id} - {self.subject}"