from django.db import models


class CompressionBatch(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("PARTIAL_FAILURE", "Partial Failure"),
        ("FAILED", "Failed"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    total_jobs = models.PositiveIntegerField(default=0)
    completed_jobs = models.PositiveIntegerField(default=0)
    failed_jobs = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Batch {self.id} - {self.status} ({self.completed_jobs}/{self.total_jobs})"


class CompressionJob(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    batch = models.ForeignKey(
        CompressionBatch,
        on_delete=models.CASCADE,
        related_name="jobs",
        null=True,
        blank=True,
    )
    original_file = models.FileField(upload_to="pdfs/original/")
    compressed_file = models.FileField(upload_to="pdfs/compressed/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Job {self.id} - {self.status}"
