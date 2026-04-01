from django.urls import path, include

urlpatterns = [
    path("api/emails/", include("apps.mailer.urls")),
]