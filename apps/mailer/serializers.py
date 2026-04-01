from rest_framework import serializers


class BulkEmailSerializer(serializers.Serializer):
    emails = serializers.ListField(
        child=serializers.EmailField(),
        max_length=100,
        allow_empty=False,
    )
    subject = serializers.CharField(max_length=255)
    body = serializers.CharField()