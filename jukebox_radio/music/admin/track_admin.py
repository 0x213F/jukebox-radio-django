import math

from django.apps import apps
from django.contrib import admin
from django.utils.html import mark_safe


class StemAdminInline(admin.TabularInline):
    model = apps.get_model("music.Stem")
    fk_name = "track"
    extra = 0

    ordering = ("instrument",)

    fields = (
        "instrument",
        "list_url",
    )
    list_display = fields
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def list_url(self, obj):
        url = obj.audio.url
        return mark_safe(f'<a href="{url}">{url}</a>')

    list_url.short_description = "URL"


class CollectionListingAdminInline(admin.TabularInline):
    model = apps.get_model("music.CollectionListing")
    fk_name = "track"
    extra = 0

    ordering = ("created_at",)

    fields = (
        "list_collection_name",
        "list_collection_provider",
        "list_collection_format",
    )
    list_display = fields
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.filter(deleted_at__isnull=True)
        return qs

    def list_collection_name(self, obj):
        url = f"../../../{obj.collection.format}/{obj.collection_id}"
        return mark_safe(f'<a href="{url}">{obj.collection.name}</a>')

    list_collection_name.short_description = "COLLECTION"

    def list_collection_provider(self, obj):
        return obj.collection.get_provider_display()

    list_collection_provider.short_description = "PROVIDER"

    def list_collection_format(self, obj):
        return obj.collection.get_format_display()

    list_collection_format.short_description = "FORMAT"


class ProviderListFilter(admin.SimpleListFilter):
    title = "provider"
    parameter_name = "provider"

    def lookups(self, request, model_admin):
        Track = apps.get_model("music", "Track")
        return Track.PROVIDER_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(provider=value)


class TrackFormatListFilter(admin.SimpleListFilter):
    title = "format"
    parameter_name = "format"

    def lookups(self, request, model_admin):
        Track = apps.get_model("music", "Track")
        return Track.FORMAT_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(format=value)


class TrackHasDurationFilter(admin.SimpleListFilter):
    title = "has duration"
    parameter_name = "has_duration"

    YES = "yes"
    NO = "no"

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
            return queryset.filter(duration_ms__isnull=False)
        elif value == "False":
            return queryset.filter(duration_ms__isnull=True)
        else:
            raise Exception("Invalid choice")


@admin.register(apps.get_model("music.Track"))
class TrackAdmin(admin.ModelAdmin):
    list_filter = (
        ProviderListFilter,
        TrackFormatListFilter,
        TrackHasDurationFilter,
    )

    inlines = (
        StemAdminInline,
        CollectionListingAdminInline,
    )

    list_display = (
        "list_uuid",
        "list_name",
        "list_album_name",
        "list_artist_name",
        "list_duration",
        "list_image",
        "provider",
        "format",
    )

    search_fields = (
        "uuid",
        "user__email",
        "name",
        "album_name",
        "artist_name",
        "external_id",
    )

    fieldsets = (
        (
            "CONTENT",
            {
                "fields": (
                    "list_image_large",
                    "list_audio",
                ),
            },
        ),
        (
            "INFORMATION",
            {
                "fields": (
                    "name",
                    "album_name",
                    "artist_name",
                ),
            },
        ),
        (
            "ABOUT",
            {
                "fields": (
                    "list_uuid",
                    "provider",
                    "format",
                ),
            },
        ),
        (
            "STATISTICS",
            {
                "fields": (
                    "duration_ms",
                    "created_at",
                    "updated_at",
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

    def list_name(self, obj):
        name = obj.name
        if len(name) < 32:
            return name

        return name[:32] + "..."

    list_name.short_description = "NAME"

    def list_album_name(self, obj):
        album_name = obj.album_name
        if len(album_name) < 32:
            return album_name

        return album_name[:32] + "..."

    list_album_name.short_description = "ALBUM NAME"

    def list_artist_name(self, obj):
        artist_name = obj.artist_name
        if len(artist_name) < 64:
            return artist_name

        return artist_name[:64] + "..."

    list_artist_name.short_description = "ARTIST NAME"

    def list_duration(self, obj):
        if not obj.duration_ms:
            return ""

        vals = []

        hours = math.floor(obj.duration_ms / (1000 * 60 * 60))
        if hours:
            vals.append(f"{hours} hours")

        minutes = math.floor(obj.duration_ms / (1000 * 60))
        if minutes:
            vals.append(f"{minutes} minutes")

        seconds = obj.duration_ms % (1000 * 60) / 1000
        if seconds:
            vals.append(f"{seconds} seconds")

        return " ".join(vals)

    list_duration.short_description = "DURATION"

    def list_image(self, obj):
        url = obj.img_url or ""  # obj.img.url
        return mark_safe(f'<img src="{url}" style="height: 15px;" />')

    list_image.short_description = "IMAGE"

    def list_image_large(self, obj):
        url = obj.img_url or obj.img.url
        return mark_safe(f'<img src="{url}" style="height: 256px;" />')

    list_image_large.short_description = "IMAGE"

    def list_audio(self, obj):
        if obj.external_id:
            return obj.external_id
        url = obj.audio.url
        return mark_safe(f'<a href="{url}">{url}</a>')

    list_audio.short_description = "AUDIO ID"
