from django.urls import path
from .views import UploadAndCompressAPIView, CompressionStatusAPIView

urlpatterns = [
    path("upload/", UploadAndCompressAPIView.as_view(), name="upload-compress"),
    path("status/<int:job_id>/", CompressionStatusAPIView.as_view(), name="compress-status"),
]