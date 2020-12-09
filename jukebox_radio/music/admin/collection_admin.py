import math

import pghistory

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from django.utils.html import mark_safe

User = get_user_model()


class CollectionListingAdminInline(admin.TabularInline):
    model = apps.get_model("music.CollectionListing")
    fk_name = "collection"
    extra = 0

    ordering = ("number",)

    fields = (
        "list_track_name",
        "list_album_name",
        "list_artist_name",
        "list_track_number",
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

    def list_track_name(self, obj):
        url = f"../../../track/{obj.track_id}"

        name = obj.track.name
        if len(name) > 64:
            name = name[:64] + "..."

        return mark_safe(f'<a href="{url}">{name}</a>')

    list_track_name.short_description = "TRACK"

    def list_album_name(self, obj):
        name = obj.track.album_name
        if len(name) > 64:
            name = name[:64] + "..."

        return name

    list_album_name.short_description = "ALBUM NAME"

    def list_artist_name(self, obj):
        name = obj.track.artist_name
        if len(name) > 64:
            name = name[:64] + "..."

        return name

    list_artist_name.short_description = "ARTIST NAME"

    def list_track_number(self, obj):
        return obj.number

    list_track_number.short_description = "TRACK NUMBER"


class ProviderListFilter(admin.SimpleListFilter):
    title = "provider"
    parameter_name = "provider"

    def lookups(self, request, model_admin):
        Collection = apps.get_model("music", "Collection")
        return Collection.PROVIDER_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(provider=value)


class CollectionFormatListFilter(admin.SimpleListFilter):
    title = "format"
    parameter_name = "format"

    def lookups(self, request, model_admin):
        Collection = apps.get_model("music", "Collection")
        return Collection.FORMAT_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(format=value)


class CollectionHasRelatedCollectionListingsFilter(admin.SimpleListFilter):
    title = "has tracks"
    parameter_name = "has_related_collection_listings"

    YES = "yes"
    NO = "no"

    def lookups(self, request, model_admin):
        return (
            (True, "Yes"),
            (False, "No"),
        )

    def queryset(self, request, queryset):
        CollectionListing = apps.get_model("music", "CollectionListing")

        value = self.value()
        if not value:
            return queryset

        if value == "True":
            return queryset.filter(
                Exists(
                    CollectionListing.objects.filter(
                        collection_id=OuterRef("uuid"),
                    )
                )
            )
        elif value == "False":
            return queryset.filter(
                ~Exists(
                    CollectionListing.objects.filter(
                        collection_id=OuterRef("uuid"),
                    )
                )
            )
        else:
            raise Exception("Invalid choice")


@admin.register(apps.get_model("music.Collection"))
class CollectionAdmin(admin.ModelAdmin):

    list_filter = (
        ProviderListFilter,
        CollectionFormatListFilter,
        CollectionHasRelatedCollectionListingsFilter,
    )

    inlines = (CollectionListingAdminInline,)

    list_display = (
        "list_uuid",
        "list_name",
        "list_artist_name",
        "list_image",
        "provider",
        "format",
    )

    fieldsets = (
        (
            "CONTENT",
            {
                "fields": ("list_image_large",),
            },
        ),
        (
            "INFORMATION",
            {
                "fields": (
                    "name",
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

    def list_uuid(self, obj):
        return mark_safe(f"<tt>{obj.uuid}</tt>")

    def list_name(self, obj):
        name = obj.name
        if len(name) < 32:
            return name

        return name[:32] + "..."

    list_name.short_description = "NAME"

    def list_artist_name(self, obj):
        artist_name = obj.artist_name
        if len(artist_name) < 64:
            return artist_name

        return artist_name[:64] + "..."

    list_artist_name.short_description = "ARTIST NAME"

    def list_image(self, obj):
        url = obj.img_url or obj.img.url
        return mark_safe(f'<img src="{url}" style="height: 15px;" />')

    list_image.short_description = "IMAGE"

    def list_image_large(self, obj):
        url = obj.img_url or obj.img.url
        return mark_safe(f'<img src="{url}" style="height: 256px;" />')

    list_image_large.short_description = "IMAGE"
