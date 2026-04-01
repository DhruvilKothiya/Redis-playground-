from django.urls import path
from .views import SendBulkEmailAPIView

urlpatterns = [
    path("send-batch/", SendBulkEmailAPIView.as_view(), name="send-batch"),
]