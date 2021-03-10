import pghistory
from django.apps import apps
from django.contrib import admin
from django.utils.html import mark_safe


@admin.register(apps.get_model("streams.Stream"))
class StreamAdmin(admin.ModelAdmin):

    list_display = (
        "list_uuid",
        "now_playing",
        "list_is_playing",
        "list_is_paused",
        "user",
    )

    search_fields = (
        "uuid",
        "user__email",
        "now_playing__track__uuid",
        "now_playing__track__name",
        "now_playing__track__artist_name",
        "now_playing__track__album_name",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def list_uuid(self, obj):
        return mark_safe(f"<tt>{obj.uuid}</tt>")

    list_uuid.short_description = "UUID"

    def list_is_playing(self, obj):
        return obj.is_playing

    list_is_playing.short_description = "IS PLAYING"
    list_is_playing.boolean = True

    def list_is_paused(self, obj):
        return obj.is_paused

    list_is_paused.short_description = "IS PAUSED"
    list_is_paused.boolean = True

    # NOTE: https://github.com/jyveapp/django-pghistory
    object_history_template = "admin/pghistory_template.html"

    def history_view(self, request, object_id, extra_context=None):
        """
        Adds additional context for the custom history template.
        """
        extra_context = extra_context or {}
        extra_context["object_history"] = (
            pghistory.models.AggregateEvent.objects.target(self.model(pk=object_id))
            .order_by("pgh_created_at")
            .select_related("pgh_context")
        )
        return super().history_view(request, object_id, extra_context=extra_context)
