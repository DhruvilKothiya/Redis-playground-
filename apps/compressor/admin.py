from django.contrib import admin
from .models import CompressionBatch, CompressionJob


class CompressionJobInline(admin.TabularInline):
    model = CompressionJob
    extra = 0
    readonly_fields = ("status", "original_file", "compressed_file", "created_at")
    can_delete = False


@admin.register(CompressionBatch)
class CompressionBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "total_jobs", "completed_jobs", "failed_jobs", "created_at", "completed_at")
    list_filter = ("status",)
    readonly_fields = ("created_at", "completed_at")
    inlines = [CompressionJobInline]


@admin.register(CompressionJob)
class CompressionJobAdmin(admin.ModelAdmin):
    list_display = ("id", "batch", "status", "original_file", "created_at")
    list_filter = ("status",)
    readonly_fields = ("created_at",)
