from django.urls import path, include

urlpatterns = [
    path("api/auth/", include("apps.users.urls")),
    path("api/emails/", include("apps.mailer.urls")),
]