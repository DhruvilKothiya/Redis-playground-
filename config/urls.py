from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("api/auth/", include("apps.users.urls")),
    path("api/emails/", include("apps.mailer.urls")),

    # NEW PDF compression APIs
    path("api/compress/", include("apps.compressor.urls")),
]

# media file serving for local development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)