from rest_framework import serializers
from .models import CompressionJob, CompressionBatch


class CompressionUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False
    )


class CompressionJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompressionJob
        fields = "__all__"


class CompressionBatchSerializer(serializers.ModelSerializer):
    jobs = CompressionJobSerializer(many=True, read_only=True)

    class Meta:
        model = CompressionBatch
        fields = [
            "id",
            "status",
            "total_jobs",
            "completed_jobs",
            "failed_jobs",
            "created_at",
            "completed_at",
            "jobs",
        ]
