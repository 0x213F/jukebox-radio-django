import math

import pghistory

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.html import mark_safe

from jukebox_radio.music.models.provider import GLOBAL_PROVIDER_CHOICES

User = get_user_model()


class CollectionListingAdminInline(admin.TabularInline):
    model = apps.get_model("music.CollectionListing")
    fk_name = "collection"
    extra = 0

    ordering = ("number",)

    fields = ('list_track_name', 'list_album_name', 'list_artist_name', 'list_track_number',)
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
        url = f'../../../track/{obj.track_id}'

        name = obj.track.name
        if len(name) > 64:
            name = name[:64] + '...'

        return mark_safe(f'<a href="{url}">{name}</a>')
    list_track_name.short_description = 'TRACK NAME'

    def list_album_name(self, obj):
        name = obj.track.album_name
        if len(name) > 64:
            name = name[:64] + '...'

        return name
    list_album_name.short_description = 'ALBUM NAME'

    def list_artist_name(self, obj):
        name = obj.track.artist_name
        if len(name) > 64:
            name = name[:64] + '...'

        return name
    list_artist_name.short_description = 'ARTIST NAME'

    def list_track_number(self, obj):
        return obj.number
    list_track_number.short_description = 'TRACK NUMBER'


class ProviderListFilter(admin.SimpleListFilter):
    title = 'provider'
    parameter_name = 'provider'

    def lookups(self, request, model_admin):
        return GLOBAL_PROVIDER_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(provider=value)


class BaseCollectionAdmin(admin.ModelAdmin):

    list_filter = (ProviderListFilter,)

    inlines = (CollectionListingAdminInline,)

    fieldsets = (
        ("CONTENT", {
            'fields': (
                'list_image_large',
            ),
        }),
        ("INFORMATION", {
            'fields': (
                'name', 'artist_name',
            ),
        }),
        ("ABOUT", {
            'fields': (
                'list_uuid', 'provider', 'format',
            ),
        }),
        ("STATISTICS", {
            'fields': (
                'created_at', 'updated_at',
            ),
        }),
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def list_uuid(self, obj):
        return mark_safe(f'<tt>{obj.uuid}</tt>')

    def list_image_large(self, obj):
        url = obj.img_url or obj.img.url
        return mark_safe(f'<img src="{url}" style="height: 256px;" />')


@admin.register(apps.get_model("music.Album"))
class AlbumAdmin(BaseCollectionAdmin):

    search_fields = (
        "uuid",
        "name",
        "artist_name",
        "external_id",
    )

    def get_queryset(self, request):
        Collection = apps.get_model('music', 'Collection')

        qs = super().get_queryset(request)
        qs = qs.filter(format=Collection.FORMAT_ALBUM)
        return qs


@admin.register(apps.get_model("music.Playlist"))
class PlaylistAdmin(BaseCollectionAdmin):

    search_fields = (
        "uuid",
        "name",
        "artist_name",
        "external_id",
    )

    def get_queryset(self, request):
        Collection = apps.get_model('music', 'Collection')

        qs = super().get_queryset(request)
        qs = qs.filter(format=Collection.FORMAT_PLAYLIST)
        return qs
