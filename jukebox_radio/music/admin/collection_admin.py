import math

import pghistory

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import mark_safe

from jukebox_radio.music.models.provider import GLOBAL_PROVIDER_CHOICES

User = get_user_model()


class CollectionListingAdminInline(admin.TabularInline):
    model = apps.get_model("music.CollectionListing")
    fk_name = "collection"
    extra = 0

    ordering = ("number",)

    fields = ('list_track_name', 'list_track_number',)

    readonly_fields = ("list_track_name", "list_track_number",)

    def has_add_permission(self, request, obj=None):
        return False

    def list_track_name(self, obj):
        url = reverse(f'admin:music_collectionlisting', obj.id)
        return mark_safe(f'<a href="{url}">{obj.track.name}</a>')
    list_track_name.short_description = 'TRACK NAME'

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


@admin.register(apps.get_model("music.Album"))
class AlbumAdmin(admin.ModelAdmin):

    inlines = (CollectionListingAdminInline,)

    search_fields = (
        "uuid",
        "name",
        "artist_name",
        "external_id",
    )

    def get_queryset(self, request):
        Collection = apps.get_model("music.Collection")
        qs = Collection.objects.all()
        qs = qs.filter(format=Collection.FORMAT_ALBUM)
        return qs

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(apps.get_model("music.Playlist"))
class PlaylistAdmin(admin.ModelAdmin):

    inlines = (CollectionListingAdminInline,)

    search_fields = (
        "uuid",
        "name",
        "artist_name",
        "external_id",
    )

    def get_queryset(self, request):
        Collection = apps.get_model("music.Collection")

        qs = Collection.objects.all()
        qs = qs.filter(format=Collection.FORMAT_PLAYLIST)
        return qs

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(apps.get_model("music.Session"))
class SessionAdmin(admin.ModelAdmin):

    inlines = (CollectionListingAdminInline,)

    search_fields = (
        "uuid",
        "name",
        "artist_name",
    )

    def get_queryset(self, request):
        Collection = apps.get_model("music", "Collection")

        qs = Collection.objects.all()
        qs = qs.filter(format=Collection.FORMAT_SESSION)
        return qs

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
