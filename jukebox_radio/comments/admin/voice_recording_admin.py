from django.apps import apps
from django.contrib import admin


@admin.register(apps.get_model("comments.VoiceRecording"))
class VoiceRecordingAdmin(admin.ModelAdmin):

    order_by = ("created_at",)

    list_display = (
        "uuid",
        "transcript_final",
        "created_at",
        "user",
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.order_by("created_at")
        return qs

    def has_add_permission(self, request, obj=None):
        return False
