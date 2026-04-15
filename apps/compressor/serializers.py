from rest_framework import serializers
from .models import CompressionJob


class CompressionUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False
    )


class CompressionJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompressionJob
        fields = "__all__"