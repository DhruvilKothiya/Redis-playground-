from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("compressor", "0001_initial"),
    ]

    operations = [
        # 1. Create the new CompressionBatch table
        migrations.CreateModel(
            name="CompressionBatch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("PROCESSING", "Processing"),
                            ("COMPLETED", "Completed"),
                            ("PARTIAL_FAILURE", "Partial Failure"),
                            ("FAILED", "Failed"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("total_jobs", models.PositiveIntegerField(default=0)),
                ("completed_jobs", models.PositiveIntegerField(default=0)),
                ("failed_jobs", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        # 2. Add nullable FK from CompressionJob → CompressionBatch
        migrations.AddField(
            model_name="compressionjob",
            name="batch",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="jobs",
                to="compressor.compressionbatch",
            ),
        ),
    ]
