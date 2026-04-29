from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.UploadAndCompressAPIView.as_view(), name="upload_compress"),
    path("batch/<int:batch_id>/", views.BatchStatusAPIView.as_view(), name="batch_status"),
    path("job/<int:job_id>/", views.CompressionStatusAPIView.as_view(), name="job_status"),
]
