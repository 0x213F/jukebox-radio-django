from django.apps import apps
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.html import mark_safe


class QueueWasPlayedFilter(admin.SimpleListFilter):
    title = "was played"
    parameter_name = "was_played"

    def lookups(self, request, model_admin):
        return (
            (True, "Yes"),
            (False, "No"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset

        if value == "True":
            return queryset.filter(played_at__isnull=False)
        elif value == "False":
            return queryset.filter(played_at__isnull=True)
        else:
            raise Exception("Invalid choice")


class QueueIsArchivedFilter(admin.SimpleListFilter):
    title = "is archived"
    parameter_name = "is_archived"

    def lookups(self, request, model_admin):
        return (
            (True, "Yes"),
            (False, "No"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset

        if value == "True":
            return queryset.filter(deleted_at__isnull=False)
        elif value == "False":
            return queryset.filter(deleted_at__isnull=True)
        else:
            raise Exception("Invalid choice")


@admin.register(apps.get_model("streams.Queue"))
class QueueAdmin(admin.ModelAdmin):
    list_filter = (
        QueueWasPlayedFilter,
        QueueIsArchivedFilter,
    )

    list_display = (
        "list_uuid",
        "list_prev",
        "list_next",
        "list_parent",
        "list_stream",
        "user",
        "list_content",
    )

    search_fields = (
        "uuid",
        "user__email",
        "track__uuid",
        "track__name",
        "track__artist_name",
        "track__album_name",
        "collection__uuid",
        "collection__name",
        "collection__artist_name",
        "stream__uuid",
        "next_queue_ptr__uuid",
        "prev_queue_ptr__uuid",
        "parent_queue_ptr__uuid",
    )

    fieldsets = (
        (
            "PLAYBACK",
            {
                "fields": (
                    "track",
                    "collection",
                    "played_at",
                ),
            },
        ),
        (
            "CONTEXT",
            {
                "fields": (
                    "prev_queue_ptr",
                    "next_queue_ptr",
                    "parent_queue_ptr",
                ),
            },
        ),
        (
            "META",
            {
                "fields": (
                    "is_abstract",
                    "is_head",
                    "created_at",
                    "updated_at",
                    "deleted_at",
                ),
            },
        ),
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

    def list_prev(self, obj):
        return mark_safe(f"<tt>{str(obj.uuid)[:8]}</tt>")

    list_uuid.short_description = "PREVIOUS"

    def list_next(self, obj):
        return mark_safe(f"<tt>{str(obj.uuid)[:8]}</tt>")

    list_uuid.short_description = "NEXT"

    def list_parent(self, obj):
        return mark_safe(f"<tt>{str(obj.uuid)[:8]}</tt>")

    list_uuid.short_description = "PARENT"

    def list_stream(self, obj):
        return mark_safe(f"<tt>{str(obj.stream_id)[:8]}</tt>")

    list_stream.short_description = "STREAM"

    def list_content(self, obj):
        return obj.track or obj.collection

    list_content.short_description = "CONTENT"
